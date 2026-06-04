from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.crypto import encrypt
from app.core.exceptions import NotFoundError, PlatformAuthError
from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.schemas.social_account import (
    InstagramMediaItem,
    MediaFeedResponse,
    SocialAccountResponse,
    SyncResponse,
    TokenRefreshResponse,
)
from app.services.instagram.service import InstagramService
from app.services.token_refresh_service import TokenRefreshService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["social_accounts"])


@router.get(
    "/devices/{device_id}/accounts",
    response_model=list[SocialAccountResponse],
)
async def list_accounts_for_device(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> list[SocialAccountResponse]:
    """Return all social accounts connected to a device."""
    repo = SocialAccountRepository(db)
    accounts = await repo.list_by_device(device_id)
    return [SocialAccountResponse.model_validate(a) for a in accounts]


@router.delete(
    "/accounts/{account_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def disconnect_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Disconnect (delete) a social account."""
    repo = SocialAccountRepository(db)
    log_repo = ActivityLogRepository(db)
    account = await repo.get(account_id)
    if account is None:
        raise NotFoundError(f"Social account {account_id} not found.")
    platform = account.platform
    username = account.username
    await repo.delete(account_id)
    await log_repo.log(
        event_type="account.disconnected",
        resource_type="social_account",
        resource_id=account_id,
        description=f"Disconnected {platform} account @{username}.",
    )


@router.post(
    "/accounts/{account_id}/sync",
    response_model=SyncResponse,
)
async def sync_account(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SyncResponse:
    """Re-sync a social account's profile from its platform."""
    repo = SocialAccountRepository(db)
    log_repo = ActivityLogRepository(db)
    account = await repo.get(account_id)
    if account is None:
        raise NotFoundError(f"Social account {account_id} not found.")

    synced = False
    if account.platform == "instagram":
        svc = InstagramService()
        profile_data = await svc.sync_profile(account)
        profile_data["last_synced_at"] = datetime.now(tz=timezone.utc)
        account = await repo.update(account_id, profile_data)
        synced = True
        await log_repo.log(
            event_type="account.synced",
            resource_type="social_account",
            resource_id=account_id,
            description=f"Synced Instagram profile for @{account.username}.",
        )
    else:
        logger.warning("Sync not implemented for platform=%s", account.platform)

    return SyncResponse(
        account=SocialAccountResponse.model_validate(account),
        synced=synced,
    )


@router.post(
    "/accounts/{account_id}/refresh-token",
    response_model=TokenRefreshResponse,
)
async def refresh_token(
    account_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TokenRefreshResponse:
    """
    Manually refresh the access token for an Instagram account.
    Instagram long-lived tokens expire after 60 days; this extends them
    by another 60 days. Safe to call repeatedly.
    """
    svc = TokenRefreshService(db)
    try:
        refreshed = await svc.refresh_account(account_id)
    except PlatformAuthError as exc:
        return TokenRefreshResponse(
            account_id=account_id,
            platform="instagram",
            refreshed=False,
            message=str(exc),
        )

    return TokenRefreshResponse(
        account_id=account_id,
        platform="instagram",
        refreshed=refreshed,
        message="Token refreshed successfully." if refreshed else "Refresh not needed or not supported.",
    )


@router.get(
    "/accounts/{account_id}/media",
    response_model=MediaFeedResponse,
)
async def get_account_media(
    account_id: uuid.UUID,
    limit: int = Query(default=12, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> MediaFeedResponse:
    """
    Fetch recent media from an Instagram account's feed.
    Only supported for Instagram Business/Creator accounts.
    """
    repo = SocialAccountRepository(db)
    account = await repo.get(account_id)
    if account is None:
        raise NotFoundError(f"Social account {account_id} not found.")

    if account.platform != "instagram":
        return MediaFeedResponse(
            account_id=account_id,
            platform=account.platform,
            items=[],
        )

    svc = InstagramService()
    raw_items = await svc.get_media_feed(account, limit=limit)

    items = [InstagramMediaItem(**item) for item in raw_items]

    return MediaFeedResponse(
        account_id=account_id,
        platform="instagram",
        items=items,
    )
