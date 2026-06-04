from __future__ import annotations

import asyncio
import logging

from app.core.config import settings
from app.core.crypto import decrypt
from app.core.exceptions import PlatformPublishError
from app.integrations.meta import instagram as ig_api
from app.models.social_account import SocialAccount
from app.models.upload import Upload

logger = logging.getLogger(__name__)

_POLL_ATTEMPTS = 10
_POLL_INTERVAL_SECONDS = 3


class InstagramService:
    """Handles publishing to Instagram via the Graph API."""

    async def publish_reel(
        self,
        upload: Upload,
        account: SocialAccount,
        caption: str,
    ) -> str:
        """
        Publish a video as an Instagram Reel.
        Returns the platform_post_id (media_id) on success.
        """
        token = decrypt(account.access_token_enc)
        ig_user_id = account.instagram_business_id or account.platform_user_id

        # The video must be publicly accessible for Instagram to fetch it.
        # We serve files via the static /media mount.  The public base is derived
        # from META_REDIRECT_URI (e.g. "http://myserver.com/api/v1/auth/meta/callback"
        # → "http://myserver.com").
        _base = settings.META_REDIRECT_URI.split("/api/")[0]
        video_url = f"{_base}/media/{upload.file_path}"

        logger.info("Creating Reel container for ig_user_id=%s", ig_user_id)
        creation_id = await ig_api.create_media_container(
            ig_user_id=ig_user_id,
            token=token,
            video_url=video_url,
            media_type="REELS",
            caption=caption,
        )

        # Poll until FINISHED.
        status = await self._poll_container(creation_id, token)
        if status != "FINISHED":
            raise PlatformPublishError(
                f"Instagram container did not finish processing (status={status}). "
                f"creation_id={creation_id}"
            )

        media_id = await ig_api.publish_container(ig_user_id, token, creation_id)
        logger.info("Reel published: media_id=%s for account=%s", media_id, account.username)
        return media_id

    async def publish_image(
        self,
        upload: Upload,
        account: SocialAccount,
        caption: str,
    ) -> str:
        """
        Publish an image to Instagram.
        Returns the platform_post_id (media_id) on success.
        """
        token = decrypt(account.access_token_enc)
        ig_user_id = account.instagram_business_id or account.platform_user_id

        _base = settings.META_REDIRECT_URI.split("/api/")[0]
        image_url = f"{_base}/media/{upload.file_path}"

        logger.info("Creating image container for ig_user_id=%s", ig_user_id)
        creation_id = await ig_api.create_media_container(
            ig_user_id=ig_user_id,
            token=token,
            image_url=image_url,
            caption=caption,
        )

        media_id = await ig_api.publish_container(ig_user_id, token, creation_id)
        logger.info("Image published: media_id=%s for account=%s", media_id, account.username)
        return media_id

    async def sync_profile(self, account: SocialAccount) -> dict:  # type: ignore[type-arg]
        """
        Re-fetch profile data from the Graph API.
        Returns a dict with the profile fields suitable for updating the DB row.
        """
        token = decrypt(account.access_token_enc)
        ig_user_id = account.instagram_business_id or account.platform_user_id

        profile = await ig_api.get_instagram_profile(ig_user_id, token)

        return {
            "username": profile.get("username", account.username),
            "display_name": profile.get("name"),
            "biography": profile.get("biography"),
            "followers_count": profile.get("followers_count", account.followers_count),
            "following_count": profile.get("follows_count", account.following_count),
            "media_count": profile.get("media_count", account.media_count),
            "profile_image_url": profile.get("profile_picture_url"),
        }

    async def get_media_feed(
        self,
        account: SocialAccount,
        limit: int = 12,
    ) -> list[dict]:  # type: ignore[type-arg]
        """
        Fetch the most recent media items from an Instagram account.
        Returns raw Graph API media objects.
        """
        token = decrypt(account.access_token_enc)
        ig_user_id = account.instagram_business_id or account.platform_user_id
        return await ig_api.get_user_media(ig_user_id, token, limit=limit)

    async def refresh_token(self, account: SocialAccount) -> dict:  # type: ignore[type-arg]
        """
        Refresh a long-lived Instagram token before it expires.
        Returns the new token data: {access_token, expires_in}.
        """
        current_token = decrypt(account.access_token_enc)
        return await ig_api.refresh_long_lived_token(current_token)

    async def _poll_container(self, creation_id: str, token: str) -> str:
        """Poll a media container until it reaches a terminal state."""
        for attempt in range(_POLL_ATTEMPTS):
            status = await ig_api.get_container_status(creation_id, token)
            logger.debug(
                "Container %s status=%s (attempt %d/%d)",
                creation_id,
                status,
                attempt + 1,
                _POLL_ATTEMPTS,
            )
            if status in ("FINISHED", "ERROR", "EXPIRED"):
                return status
            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
        return "TIMEOUT"
