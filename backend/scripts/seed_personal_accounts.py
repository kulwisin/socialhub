"""
Seed the database with personal Instagram and Facebook accounts from .env.
Run once after migrations:  python -m scripts.seed_personal_accounts
"""
from __future__ import annotations

import asyncio
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Load .env before any app imports so os.environ is populated
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.core.config import settings
from app.core.crypto import encrypt
from app.db.session import AsyncSessionFactory
from app.models.device import Device
from app.models.social_account import SocialAccount
from sqlalchemy import select


async def seed() -> None:
    if not settings.META_USER_ACCESS_TOKEN:
        print("ERROR: META_USER_ACCESS_TOKEN is not set in .env")
        sys.exit(1)
    if not settings.META_PAGE_ACCESS_TOKEN:
        print("ERROR: META_PAGE_ACCESS_TOKEN is not set in .env")
        sys.exit(1)
    if not settings.META_PAGE_ID:
        print("ERROR: META_PAGE_ID is not set in .env")
        sys.exit(1)
    if not settings.META_IG_ACCOUNT_ID:
        print("ERROR: META_IG_ACCOUNT_ID is not set in .env")
        sys.exit(1)

    expires_at = datetime.now(tz=timezone.utc) + timedelta(days=59)

    async with AsyncSessionFactory() as db:
        # 1 — Get or create the default device
        result = await db.execute(select(Device).where(Device.name == "My Accounts"))
        device = result.scalar_one_or_none()
        if device is None:
            device = Device(name="My Accounts", description="Personal social accounts")
            db.add(device)
            await db.flush()
            print(f"Created device: {device.id}")
        else:
            print(f"Using existing device: {device.id}")

        # 2 — Upsert Instagram account
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.device_id == device.id,
                SocialAccount.platform == "instagram",
            )
        )
        ig_account = result.scalar_one_or_none()
        if ig_account is None:
            ig_account = SocialAccount(
                device_id=device.id,
                platform="instagram",
                platform_user_id=settings.META_IG_ACCOUNT_ID,
                username="kay_singh",
                display_name="Kay Singh",
                access_token_enc=encrypt(settings.META_USER_ACCESS_TOKEN),
                facebook_page_id=settings.META_PAGE_ID,
                instagram_business_id=settings.META_IG_ACCOUNT_ID,
                token_expires_at=expires_at,
                scopes=[
                    "instagram_basic",
                    "instagram_content_publish",
                    "pages_show_list",
                    "pages_read_engagement",
                    "pages_manage_posts",
                ],
                is_active=True,
            )
            db.add(ig_account)
            print(f"Created Instagram account: {settings.META_IG_ACCOUNT_ID}")
        else:
            ig_account.access_token_enc = encrypt(settings.META_USER_ACCESS_TOKEN)
            ig_account.token_expires_at = expires_at
            ig_account.instagram_business_id = settings.META_IG_ACCOUNT_ID
            ig_account.facebook_page_id = settings.META_PAGE_ID
            print(f"Updated Instagram account: {settings.META_IG_ACCOUNT_ID}")

        # 3 — Upsert Facebook account
        result = await db.execute(
            select(SocialAccount).where(
                SocialAccount.device_id == device.id,
                SocialAccount.platform == "facebook",
            )
        )
        fb_account = result.scalar_one_or_none()
        if fb_account is None:
            fb_account = SocialAccount(
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
            db.add(fb_account)
            print(f"Created Facebook account: page_id={settings.META_PAGE_ID}")
        else:
            fb_account.access_token_enc = encrypt(settings.META_USER_ACCESS_TOKEN)
            fb_account.refresh_token_enc = encrypt(settings.META_PAGE_ACCESS_TOKEN)
            fb_account.token_expires_at = expires_at
            fb_account.facebook_page_id = settings.META_PAGE_ID
            print(f"Updated Facebook account: page_id={settings.META_PAGE_ID}")

        await db.commit()
        print("\nDone. Accounts seeded successfully.")
        print(f"  Instagram IG account ID : {settings.META_IG_ACCOUNT_ID}")
        print(f"  Facebook  Page ID       : {settings.META_PAGE_ID}")
        print(f"  Token expires at        : {expires_at.date()}")


if __name__ == "__main__":
    asyncio.run(seed())
