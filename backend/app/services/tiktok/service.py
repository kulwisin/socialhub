from __future__ import annotations

from app.models.social_account import SocialAccount
from app.models.upload import Upload


class TikTokService:
    """TikTok publishing — coming soon."""

    async def publish_video(
        self,
        upload: Upload,
        account: SocialAccount,
        caption: str,
    ) -> str:
        raise NotImplementedError("TikTok integration coming soon")
