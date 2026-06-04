from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import decrypt, encrypt
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.services.instagram.service import InstagramService

logger = logging.getLogger(__name__)

# Refresh tokens when they have fewer than this many days remaining.
_REFRESH_THRESHOLD_DAYS = 10


class TokenRefreshService:
    """
    Handles refreshing expiring platform tokens.

    Instagram long-lived tokens are valid for 60 days and can be refreshed
    at any point after the first 24 hours via the ig_refresh_token grant.
    """

    def __init__(self, session: AsyncSession) -> None:
        self.account_repo = SocialAccountRepository(session)
        self.log_repo = ActivityLogRepository(session)
        self.instagram_svc = InstagramService()

    async def refresh_account(self, account_id: object) -> bool:
        """
        Refresh the token for a single account. Returns True if refreshed.
        Raises on API failure so the caller can handle or log.
        """
        import uuid as _uuid

        account = await self.account_repo.get(_uuid.UUID(str(account_id)))
        if account is None:
            logger.warning("Token refresh: account %s not found.", account_id)
            return False

        if account.platform != "instagram":
            logger.info(
                "Token refresh not implemented for platform=%s", account.platform
            )
            return False

        token_data = await self.instagram_svc.refresh_token(account)
        new_token: str = token_data["access_token"]
        expires_in: int = token_data.get("expires_in", 5_184_000)  # 60 days

        await self.account_repo.update(
            account.id,
            {
                "access_token_enc": encrypt(new_token),
                "token_expires_at": datetime.now(tz=timezone.utc)
                + timedelta(seconds=expires_in),
            },
        )

        await self.log_repo.log(
            event_type="account.token_refreshed",
            resource_type="social_account",
            resource_id=account.id,
            description=(
                f"Instagram token refreshed for @{account.username}. "
                f"New expiry in {expires_in // 86400} days."
            ),
            metadata={"platform": "instagram", "expires_in": expires_in},
        )

        logger.info(
            "Refreshed Instagram token for account %s (@%s).",
            account.id,
            account.username,
        )
        return True

    async def refresh_expiring_accounts(self) -> dict[str, int]:
        """
        Scan all accounts and refresh tokens expiring within the threshold.
        Returns counts: {refreshed, skipped, failed}.
        Intended to be called by a scheduled job or startup hook.
        """
        threshold = datetime.now(tz=timezone.utc) + timedelta(
            days=_REFRESH_THRESHOLD_DAYS
        )
        accounts = await self.account_repo.list(limit=500)

        refreshed = skipped = failed = 0

        for account in accounts:
            if account.platform != "instagram":
                skipped += 1
                continue
            if account.token_expires_at is None:
                skipped += 1
                continue
            expires = account.token_expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            if expires > threshold:
                skipped += 1
                continue

            try:
                await self.refresh_account(account.id)
                refreshed += 1
            except Exception:
                logger.exception(
                    "Failed to refresh token for account %s", account.id
                )
                failed += 1

        logger.info(
            "Token refresh sweep complete: refreshed=%d skipped=%d failed=%d",
            refreshed,
            skipped,
            failed,
        )
        return {"refreshed": refreshed, "skipped": skipped, "failed": failed}
