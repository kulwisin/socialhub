from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from app.core.exceptions import NotFoundError, ValidationError
from app.models.social_account import SocialAccount
from app.models.upload import Upload
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.post_repository import PostRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.post import PostResponse, PublishRequest, PublishResponse
from app.services.facebook.service import FacebookService
from app.services.instagram.service import InstagramService
from app.services.tiktok.service import TikTokService

logger = logging.getLogger(__name__)


class PublisherService:
    """
    Orchestrates publishing an upload to one or more social accounts.
    Each account gets its own Post row and is dispatched to the correct
    platform service.
    """

    def __init__(
        self,
        upload_repo: UploadRepository,
        social_account_repo: SocialAccountRepository,
        post_repo: PostRepository,
        log_repo: ActivityLogRepository,
        instagram_svc: InstagramService | None = None,
        facebook_svc: FacebookService | None = None,
        tiktok_svc: TikTokService | None = None,
    ) -> None:
        self.upload_repo = upload_repo
        self.social_account_repo = social_account_repo
        self.post_repo = post_repo
        self.log_repo = log_repo
        self.instagram_svc = instagram_svc or InstagramService()
        self.facebook_svc = facebook_svc or FacebookService()
        self.tiktok_svc = tiktok_svc or TikTokService()

    async def publish(self, request: PublishRequest) -> PublishResponse:
        """
        Publish an upload to each of the requested accounts.
        Returns a PublishResponse describing the outcome of each attempt.
        """
        upload = await self.upload_repo.get(request.upload_id)
        if upload is None:
            raise NotFoundError(f"Upload {request.upload_id} not found.")
        if upload.status != "ready":
            raise ValidationError(
                f"Upload {upload.id} is not ready for publishing (status={upload.status!r})."
            )

        accounts = await self.social_account_repo.get_active_for_publish(request.account_ids)
        account_map: dict[uuid.UUID, SocialAccount] = {a.id: a for a in accounts}

        post_responses: list[PostResponse] = []
        succeeded = 0
        failed = 0

        for account_id in request.account_ids:
            account = account_map.get(account_id)
            if account is None:
                # Account not found or inactive — create a failed post record.
                post = await self.post_repo.create(
                    {
                        "upload_id": upload.id,
                        "social_account_id": account_id,
                        "caption": request.caption,
                        "status": "failed",
                        "error_message": "Account not found or inactive.",
                    }
                )
                failed += 1
                await self.log_repo.log(
                    event_type="post.failed",
                    resource_type="post",
                    resource_id=post.id,
                    description=f"Publish skipped — account {account_id} not found or inactive.",
                    metadata={"upload_id": str(upload.id), "account_id": str(account_id)},
                )
                post_responses.append(PostResponse.model_validate(post))
                continue

            # Create a queued post record.
            post = await self.post_repo.create(
                {
                    "upload_id": upload.id,
                    "social_account_id": account.id,
                    "caption": request.caption,
                    "status": "queued",
                }
            )

            # Dispatch to the platform service.
            platform_post_id, error_message = await self._dispatch(
                upload=upload,
                account=account,
                caption=request.caption or upload.caption or "",
            )

            if platform_post_id:
                updated_post = await self.post_repo.update(
                    post.id,
                    {
                        "status": "published",
                        "platform_post_id": platform_post_id,
                        "published_at": datetime.now(tz=timezone.utc),
                    },
                )
                succeeded += 1
                await self.log_repo.log(
                    event_type="post.published",
                    resource_type="post",
                    resource_id=post.id,
                    description=(
                        f"Published to {account.platform} as @{account.username}. "
                        f"platform_post_id={platform_post_id}"
                    ),
                    metadata={
                        "upload_id": str(upload.id),
                        "account_id": str(account.id),
                        "platform": account.platform,
                        "platform_post_id": platform_post_id,
                    },
                )
            else:
                updated_post = await self.post_repo.update(
                    post.id,
                    {
                        "status": "failed",
                        "error_message": error_message,
                    },
                )
                failed += 1
                await self.log_repo.log(
                    event_type="post.failed",
                    resource_type="post",
                    resource_id=post.id,
                    description=(
                        f"Publish to {account.platform} failed for @{account.username}."
                    ),
                    metadata={
                        "upload_id": str(upload.id),
                        "account_id": str(account.id),
                        "platform": account.platform,
                        "error": error_message,
                    },
                )

            post_responses.append(PostResponse.model_validate(updated_post))

        return PublishResponse(posts=post_responses, succeeded=succeeded, failed=failed)

    async def _dispatch(
        self,
        upload: Upload,
        account: SocialAccount,
        caption: str,
    ) -> tuple[str | None, str | None]:
        """
        Call the correct platform service. Returns (platform_post_id, None) on
        success or (None, error_message) on failure.
        """
        try:
            if account.platform == "instagram":
                if upload.media_type == "image":
                    pid = await self.instagram_svc.publish_image(upload, account, caption)
                else:
                    pid = await self.instagram_svc.publish_reel(upload, account, caption)
                return pid, None

            if account.platform == "facebook":
                pid = await self.facebook_svc.publish_video(upload, account, caption)
                return pid, None

            if account.platform == "tiktok":
                pid = await self.tiktok_svc.publish_video(upload, account, caption)
                return pid, None

            return None, f"Unsupported platform: {account.platform}"

        except NotImplementedError as exc:
            return None, str(exc)
        except Exception as exc:
            logger.exception(
                "Publish failed for account %s on platform %s",
                account.id,
                account.platform,
            )
            return None, str(exc)
