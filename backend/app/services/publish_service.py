from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone

from app.core.crypto import decrypt
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.post_repository import PostRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.post import PostResponse, PublishRequest

logger = logging.getLogger(__name__)


class PublishService:
    def __init__(
        self,
        upload_repo: UploadRepository,
        account_repo: SocialAccountRepository,
        post_repo: PostRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self._uploads = upload_repo
        self._accounts = account_repo
        self._posts = post_repo
        self._logs = log_repo

    # ------------------------------------------------------------------
    # Internal: per-platform publish stubs / real implementations
    # ------------------------------------------------------------------

    async def _publish_instagram(
        self,
        post_id: uuid.UUID,
        account_id: uuid.UUID,
        access_token_enc: str,
        ig_user_id: str | None,
        upload_file_path: str,
        caption: str | None,
    ) -> str:
        """
        Attempt to publish to Instagram via Meta Graph API.
        Falls back to a stub if IG business ID is unavailable.
        """
        if not ig_user_id:
            logger.warning(
                "Post %s: instagram_business_id not set — using stub publish.", post_id
            )
            return f"stub_ig_{uuid.uuid4().hex[:12]}"

        try:
            from app.core.config import settings
            from app.integrations.meta.instagram import (
                create_media_container,
                get_container_status,
                publish_container,
            )

            token = decrypt(access_token_enc)
            media_url = f"{settings.META_REDIRECT_URI.rsplit('/api', 1)[0]}/media/{upload_file_path}"

            creation_id = await create_media_container(
                ig_user_id,
                token,
                video_url=media_url,
                caption=caption or "",
                media_type="REELS",
            )

            # Poll for container readiness (max ~5 minutes)
            for attempt in range(60):
                status = await get_container_status(creation_id, token)
                if status == "FINISHED":
                    break
                if status == "ERROR":
                    raise RuntimeError(f"Instagram container {creation_id} errored.")
                if status == "EXPIRED":
                    raise RuntimeError(f"Instagram container {creation_id} expired.")
                await asyncio.sleep(5)
            else:
                raise RuntimeError("Instagram container timed out after 5 minutes.")

            media_id = await publish_container(ig_user_id, token, creation_id)
            return media_id
        except Exception as exc:
            logger.exception("Instagram publish failed for post %s: %s", post_id, exc)
            raise

    async def _publish_stub(self, platform: str) -> str:
        """Return a fake platform_post_id for platforms without a real implementation."""
        await asyncio.sleep(0)  # yield to event loop
        return f"stub_{platform}_{uuid.uuid4().hex[:12]}"

    async def _dispatch_to_platform(
        self,
        platform: str,
        post_id: uuid.UUID,
        account_id: uuid.UUID,
        access_token_enc: str,
        ig_user_id: str | None,
        upload_file_path: str,
        caption: str | None,
    ) -> str:
        if platform == "instagram":
            return await self._publish_instagram(
                post_id, account_id, access_token_enc, ig_user_id, upload_file_path, caption
            )
        return await self._publish_stub(platform)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def publish(
        self,
        user_id: uuid.UUID,
        req: PublishRequest,
    ) -> list[PostResponse]:
        """
        Create one Post row per account_id (status=queued), then attempt
        to publish to each platform, updating status to published/failed.
        """
        # Verify upload belongs to the user
        upload = await self._uploads.get(req.upload_id)
        if upload is None or upload.user_id != user_id:
            raise NotFoundError(f"Upload {req.upload_id} not found.")

        # Apply any override metadata to the upload
        patch: dict = {}
        if req.title is not None:
            patch["title"] = req.title
        if req.description is not None:
            patch["description"] = req.description
        if req.hashtags is not None:
            patch["hashtags"] = req.hashtags
        if patch:
            upload = await self._uploads.update(req.upload_id, patch) or upload

        # Verify accounts belong to the user
        accounts = await self._accounts.get_active_for_publish(req.account_ids)
        account_map = {a.id: a for a in accounts}

        unknown_ids = [
            str(aid) for aid in req.account_ids if aid not in account_map
        ]
        if unknown_ids:
            raise ValidationError(
                f"The following account IDs are not found or inactive: {unknown_ids}"
            )

        # Verify all accounts belong to this user
        for account in accounts:
            if account.user_id != user_id:
                raise ValidationError(
                    f"Account {account.id} does not belong to the authenticated user."
                )

        # Create queued Post rows
        posts = []
        for account in accounts:
            caption = req.caption
            if caption is None and upload.hashtags:
                caption = " ".join(f"#{h.lstrip('#')}" for h in upload.hashtags)

            post = await self._posts.create(
                {
                    "upload_id": req.upload_id,
                    "social_account_id": account.id,
                    "caption": caption,
                    "status": "queued",
                }
            )
            posts.append(post)

        # Attempt publishing for each post
        results: list[PostResponse] = []
        for post, account in zip(posts, accounts, strict=True):
            try:
                await self._posts.update(post.id, {"status": "publishing"})

                platform_post_id = await self._dispatch_to_platform(
                    platform=account.platform,
                    post_id=post.id,
                    account_id=account.id,
                    access_token_enc=account.access_token_enc,
                    ig_user_id=account.instagram_business_id,
                    upload_file_path=upload.file_path,
                    caption=post.caption,
                )

                updated = await self._posts.update(
                    post.id,
                    {
                        "status": "published",
                        "platform_post_id": platform_post_id,
                        "published_at": datetime.now(timezone.utc),
                    },
                )
                await self._logs.log(
                    event_type="post.published",
                    resource_type="post",
                    resource_id=post.id,
                    description=f"Published to {account.platform} @{account.username}",
                    metadata={
                        "platform": account.platform,
                        "platform_post_id": platform_post_id,
                        "upload_id": str(req.upload_id),
                    },
                )
            except Exception as exc:
                error_msg = str(exc)
                updated = await self._posts.update(
                    post.id,
                    {
                        "status": "failed",
                        "error_message": error_msg,
                    },
                )
                await self._logs.log(
                    event_type="post.failed",
                    resource_type="post",
                    resource_id=post.id,
                    description=f"Publish to {account.platform} @{account.username} failed",
                    metadata={"platform": account.platform, "error": error_msg},
                )
                logger.error(
                    "Publish failed for post %s on %s: %s",
                    post.id,
                    account.platform,
                    exc,
                )
            results.append(PostResponse.model_validate(updated or post))

        return results

    async def list_posts(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[PostResponse]:
        posts = await self._posts.list_by_user(user_id, skip=skip, limit=limit)
        return [PostResponse.model_validate(p) for p in posts]

    async def get_post(
        self,
        user_id: uuid.UUID,
        post_id: uuid.UUID,
    ) -> PostResponse:
        post = await self._posts.get(post_id)
        if post is None:
            raise NotFoundError(f"Post {post_id} not found.")

        # Verify ownership via the upload
        upload = await self._uploads.get(post.upload_id)
        if upload is None or upload.user_id != user_id:
            raise NotFoundError(f"Post {post_id} not found.")

        return PostResponse.model_validate(post)
