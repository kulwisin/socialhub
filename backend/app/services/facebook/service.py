from __future__ import annotations

import logging
from pathlib import Path

from app.core.config import settings
from app.core.crypto import decrypt
from app.integrations.meta import facebook as fb_api
from app.models.social_account import SocialAccount
from app.models.upload import Upload

logger = logging.getLogger(__name__)


class FacebookService:
    """Handles publishing to Facebook Pages via the Graph API."""

    async def publish_video(
        self,
        upload: Upload,
        account: SocialAccount,
        caption: str,
    ) -> str:
        """
        Upload a video to the Facebook Page and return the resulting post_id.
        The page access token is stored in refresh_token_enc (long-lived page token).
        Falls back to access_token_enc if refresh_token_enc is not set.
        """
        if account.refresh_token_enc:
            page_token = decrypt(account.refresh_token_enc)
        else:
            page_token = decrypt(account.access_token_enc)

        page_id = account.facebook_page_id or account.platform_user_id
        video_path = str(Path(settings.MEDIA_DIR) / upload.file_path)

        logger.info(
            "Publishing video to Facebook page_id=%s for account=%s",
            page_id,
            account.username,
        )

        post_id = await fb_api.publish_video_to_page(
            page_id=page_id,
            page_token=page_token,
            video_path=video_path,
            description=caption,
        )

        logger.info("Facebook video published: post_id=%s", post_id)
        return post_id
