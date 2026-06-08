"""Admin endpoints — personal-use helpers for seeding accounts and checking status."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.crypto import encrypt
from app.db.session import get_db
from app.models.device import Device
from app.models.social_account import SocialAccount

router = APIRouter(prefix="/admin", tags=["admin"])


class SeedResponse(BaseModel):
    message: str
    instagram_account_id: str
    facebook_page_id: str
    token_expires_at: str


class StatusResponse(BaseModel):
    instagram: dict  # type: ignore[type-arg]
    facebook: dict  # type: ignore[type-arg]


@router.post("/seed-accounts", response_model=SeedResponse, status_code=status.HTTP_200_OK)
async def seed_accounts(db: AsyncSession = Depends(get_db)) -> SeedResponse:
    """
    Seed (or refresh) Instagram and Facebook accounts from .env tokens.
    Safe to call multiple times — it upserts, never duplicates.
    """
    for var in ("META_USER_ACCESS_TOKEN", "META_PAGE_ACCESS_TOKEN", "META_PAGE_ID", "META_IG_ACCOUNT_ID"):
        if not getattr(settings, var):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"{var} is not configured in .env",
            )

    expires_at = datetime.now(tz=timezone.utc) + timedelta(days=59)

    # Get or create device
    result = await db.execute(select(Device).where(Device.name == "My Accounts"))
    device = result.scalar_one_or_none()
    if device is None:
        device = Device(name="My Accounts", description="Personal social accounts")
        db.add(device)
        await db.flush()

    # Upsert Instagram
    result = await db.execute(
        select(SocialAccount).where(
            SocialAccount.device_id == device.id,
            SocialAccount.platform == "instagram",
        )
    )
    ig = result.scalar_one_or_none()
    if ig is None:
        ig = SocialAccount(
            device_id=device.id,
            platform="instagram",
            platform_user_id=settings.META_IG_ACCOUNT_ID,
            username="kay_singh",
            display_name="Kay Singh",
            access_token_enc=encrypt(settings.META_USER_ACCESS_TOKEN),
            facebook_page_id=settings.META_PAGE_ID,
            instagram_business_id=settings.META_IG_ACCOUNT_ID,
            token_expires_at=expires_at,
            scopes=["instagram_basic", "instagram_content_publish", "pages_show_list", "pages_read_engagement", "pages_manage_posts"],
            is_active=True,
        )
        db.add(ig)
    else:
        ig.access_token_enc = encrypt(settings.META_USER_ACCESS_TOKEN)
        ig.token_expires_at = expires_at
        ig.instagram_business_id = settings.META_IG_ACCOUNT_ID
        ig.facebook_page_id = settings.META_PAGE_ID

    # Upsert Facebook
    result = await db.execute(
        select(SocialAccount).where(
            SocialAccount.device_id == device.id,
            SocialAccount.platform == "facebook",
        )
    )
    fb = result.scalar_one_or_none()
    if fb is None:
        fb = SocialAccount(
            device_id=device.id,
            platform="facebook",
            platform_user_id=settings.META_PAGE_ID,
            username="Kay Singh",
            display_name="Kay Singh",
            access_token_enc=encrypt(settings.META_USER_ACCESS_TOKEN),
            refresh_token_enc=encrypt(settings.META_PAGE_ACCESS_TOKEN),
            facebook_page_id=settings.META_PAGE_ID,
            token_expires_at=expires_at,
            scopes=["pages_manage_posts", "pages_show_list", "pages_read_engagement"],
            is_active=True,
        )
        db.add(fb)
    else:
        fb.access_token_enc = encrypt(settings.META_USER_ACCESS_TOKEN)
        fb.refresh_token_enc = encrypt(settings.META_PAGE_ACCESS_TOKEN)
        fb.token_expires_at = expires_at
        fb.facebook_page_id = settings.META_PAGE_ID

    await db.commit()

    return SeedResponse(
        message="Accounts seeded successfully.",
        instagram_account_id=settings.META_IG_ACCOUNT_ID,
        facebook_page_id=settings.META_PAGE_ID,
        token_expires_at=expires_at.strftime("%Y-%m-%d"),
    )


@router.get("/status", response_model=StatusResponse)
async def get_status(db: AsyncSession = Depends(get_db)) -> StatusResponse:
    """Show current status of Instagram and Facebook accounts."""
    result = await db.execute(
        select(SocialAccount).where(SocialAccount.platform.in_(["instagram", "facebook"]))
    )
    accounts = result.scalars().all()
    account_map = {a.platform: a for a in accounts}

    def _fmt(a: SocialAccount | None) -> dict:  # type: ignore[type-arg]
        if a is None:
            return {"connected": False}
        days_left = None
        if a.token_expires_at:
            delta = a.token_expires_at - datetime.now(tz=timezone.utc)
            days_left = max(0, delta.days)
        return {
            "connected": True,
            "username": a.username,
            "is_active": a.is_active,
            "token_expires_at": a.token_expires_at.strftime("%Y-%m-%d") if a.token_expires_at else None,
            "days_until_expiry": days_left,
        }

    return StatusResponse(
        instagram=_fmt(account_map.get("instagram")),
        facebook=_fmt(account_map.get("facebook")),
    )
