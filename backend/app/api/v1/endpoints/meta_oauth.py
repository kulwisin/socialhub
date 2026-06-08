from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.crypto import encrypt
from app.core.exceptions import PlatformAuthError
from app.db.session import get_db
from app.integrations.meta import instagram as ig_api
from app.integrations.meta.facebook import get_page_long_lived_token
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.social_account_repository import SocialAccountRepository

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth/meta", tags=["oauth"])

_SCOPES = [
    "public_profile",
    "pages_show_list",
    "pages_read_engagement",
    "instagram_content_publish",
]


@router.get("/authorize")
async def meta_authorize(device_id: uuid.UUID = Query(...)) -> dict[str, str]:
    """
    Return the Facebook OAuth dialog URL the user should visit.
    state = device_id (UUID string) so we can link the accounts after callback.
    """
    url = ig_api.get_authorization_url(
        app_id=settings.META_APP_ID,
        redirect_uri=settings.META_REDIRECT_URI,
        state=str(device_id),
        scopes=_SCOPES,
    )
    return {"url": url}


@router.get("/callback")
async def meta_callback(
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db),
) -> RedirectResponse:
    """
    Handle the OAuth callback from Facebook:
    1. Exchange code for short-lived token.
    2. Exchange for long-lived user token.
    3. Fetch Facebook Pages.
    4. For each page, look for linked Instagram Business Account.
    5. Upsert SocialAccount rows.
    6. Redirect to the frontend.
    """
    device_id = uuid.UUID(state)
    account_repo = SocialAccountRepository(db)
    log_repo = ActivityLogRepository(db)

    # Step 1 + 2: tokens
    try:
        short = await ig_api.exchange_code_for_token(
            app_id=settings.META_APP_ID,
            app_secret=settings.META_APP_SECRET,
            redirect_uri=settings.META_REDIRECT_URI,
            code=code,
        )
        short_token: str = short["access_token"]

        long_token_data = await ig_api.exchange_for_long_lived_token(
            app_id=settings.META_APP_ID,
            app_secret=settings.META_APP_SECRET,
            short_token=short_token,
        )
        user_token: str = long_token_data["access_token"]
        expires_in: int = long_token_data.get("expires_in", 5184000)  # 60 days default
        token_expires_at = datetime.now(tz=timezone.utc) + timedelta(seconds=expires_in)

    except Exception as exc:
        logger.exception("Meta token exchange failed for device %s", device_id)
        raise PlatformAuthError(f"Token exchange failed: {exc}") from exc

    # Step 3: Facebook Pages
    pages = await ig_api.get_user_pages(user_token)

    connected_platforms: list[str] = []

    for page in pages:
        page_id: str = page["id"]
        page_name: str = page.get("name", page_id)
        page_token: str = page.get("access_token", user_token)

        # Make the page token long-lived / never-expiring.
        try:
            page_token = await get_page_long_lived_token(
                page_token=page_token,
                app_id=settings.META_APP_ID,
                app_secret=settings.META_APP_SECRET,
            )
        except Exception:
            logger.warning("Could not extend page token for page %s; using original.", page_id)

        # Step 4: Instagram Business Account for this page.
        ig_account = await ig_api.get_instagram_account_for_page(page_id, page_token)

        if ig_account:
            ig_user_id: str = ig_account["id"]
            try:
                ig_profile = await ig_api.get_instagram_profile(ig_user_id, user_token)
            except Exception:
                ig_profile = {}

            ig_data = {
                "device_id": device_id,
                "platform": "instagram",
                "platform_user_id": ig_user_id,
                "username": ig_profile.get("username", ig_user_id),
                "display_name": ig_profile.get("name"),
                "biography": ig_profile.get("biography"),
                "followers_count": ig_profile.get("followers_count", 0),
                "following_count": ig_profile.get("follows_count", 0),
                "media_count": ig_profile.get("media_count", 0),
                "profile_image_url": ig_profile.get("profile_picture_url"),
                "access_token_enc": encrypt(user_token),
                "token_expires_at": token_expires_at,
                "scopes": _SCOPES,
                "facebook_page_id": page_id,
                "instagram_business_id": ig_user_id,
                "is_active": True,
                "last_synced_at": datetime.now(tz=timezone.utc),
            }

            existing_ig = await account_repo.get_by_device_and_platform(device_id, "instagram")
            if existing_ig:
                await account_repo.update(existing_ig.id, ig_data)
            else:
                await account_repo.create(ig_data)

            connected_platforms.append("instagram")

        # Step 5: Facebook Page account.
        fb_data = {
            "device_id": device_id,
            "platform": "facebook",
            "platform_user_id": page_id,
            "username": page_name,
            "display_name": page_name,
            "access_token_enc": encrypt(user_token),
            "refresh_token_enc": encrypt(page_token),
            "token_expires_at": None,  # page tokens don't expire after exchange
            "scopes": _SCOPES,
            "facebook_page_id": page_id,
            "is_active": True,
            "last_synced_at": datetime.now(tz=timezone.utc),
        }

        existing_fb = await account_repo.get_by_device_and_platform(device_id, "facebook")
        if existing_fb:
            await account_repo.update(existing_fb.id, fb_data)
        else:
            await account_repo.create(fb_data)

        connected_platforms.append("facebook")

    # Log the connection event.
    await log_repo.log(
        event_type="account.connected",
        resource_type="device",
        resource_id=device_id,
        description=f"Meta OAuth completed for device {device_id}. "
        f"Connected: {', '.join(set(connected_platforms)) or 'none'}.",
        metadata={"platforms": list(set(connected_platforms)), "page_count": len(pages)},
    )

    # Redirect to the frontend device detail page.
    redirect_url = f"{settings.ALLOWED_ORIGINS[0]}/devices/{device_id}?connected=true"
    return RedirectResponse(url=redirect_url, status_code=302)
