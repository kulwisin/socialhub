from __future__ import annotations

import urllib.parse
from typing import Any

from app.integrations.meta.client import MetaGraphClient

_DIALOG_BASE = "https://www.facebook.com/dialog/oauth"
_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"
_LONG_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"


def get_authorization_url(
    app_id: str,
    redirect_uri: str,
    state: str,
    scopes: list[str] | None = None,
) -> str:
    """Build the Facebook OAuth dialog URL for Instagram permissions."""
    if scopes is None:
        scopes = [
            "instagram_basic",
            "instagram_content_publish",
            "pages_show_list",
            "pages_read_engagement",
            "business_management",
        ]
    params = {
        "client_id": app_id,
        "redirect_uri": redirect_uri,
        "scope": ",".join(scopes),
        "response_type": "code",
        "state": state,
    }
    return f"{_DIALOG_BASE}?{urllib.parse.urlencode(params)}"


async def exchange_code_for_token(
    app_id: str,
    app_secret: str,
    redirect_uri: str,
    code: str,
) -> dict[str, Any]:
    """Exchange an OAuth authorization code for a short-lived user token."""
    import httpx

    params = {
        "client_id": app_id,
        "client_secret": app_secret,
        "redirect_uri": redirect_uri,
        "code": code,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(_TOKEN_URL, params=params)
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]


async def exchange_for_long_lived_token(
    app_id: str,
    app_secret: str,
    short_token: str,
) -> dict[str, Any]:
    """
    Exchange a short-lived token for a 60-day long-lived token.
    Returns dict with keys: access_token, token_type, expires_in.
    """
    import httpx

    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_token,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(_LONG_TOKEN_URL, params=params)
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]


async def get_user_pages(user_token: str) -> list[dict[str, Any]]:
    """Return the Facebook Pages managed by the authenticated user."""
    client = MetaGraphClient(access_token=user_token)
    data = await client.get(
        "/me/accounts",
        params={"fields": "id,name,access_token,instagram_business_account"},
    )
    return data.get("data", [])  # type: ignore[no-any-return]


async def get_instagram_account_for_page(
    page_id: str,
    page_token: str,
) -> dict[str, Any] | None:
    """
    Return the Instagram Business Account linked to a Facebook Page, or None.
    """
    client = MetaGraphClient(access_token=page_token)
    data = await client.get(
        f"/{page_id}",
        params={"fields": "instagram_business_account"},
    )
    ig = data.get("instagram_business_account")
    if not ig or "id" not in ig:
        return None
    return ig  # type: ignore[no-any-return]


async def get_instagram_profile(ig_user_id: str, token: str) -> dict[str, Any]:
    """Fetch the Instagram Business Account profile fields."""
    client = MetaGraphClient(access_token=token)
    return await client.get(
        f"/{ig_user_id}",
        params={
            "fields": (
                "username,name,biography,"
                "followers_count,follows_count,media_count,"
                "profile_picture_url"
            )
        },
    )


async def create_media_container(
    ig_user_id: str,
    token: str,
    **kwargs: Any,
) -> str:
    """
    Create a media container for an Instagram post.
    kwargs are passed directly as form fields (e.g. video_url=, image_url=, caption=).
    Returns the creation_id string.
    """
    client = MetaGraphClient(access_token=token)
    data = await client.post(f"/{ig_user_id}/media", data=dict(kwargs))
    return str(data["id"])


async def get_container_status(creation_id: str, token: str) -> str:
    """
    Return the status_code string of a media container.
    Possible values: IN_PROGRESS, FINISHED, ERROR, EXPIRED.
    """
    client = MetaGraphClient(access_token=token)
    data = await client.get(
        f"/{creation_id}",
        params={"fields": "status_code"},
    )
    return str(data.get("status_code", "UNKNOWN"))


async def publish_container(ig_user_id: str, token: str, creation_id: str) -> str:
    """
    Publish a finished media container. Returns the published media_id.
    """
    client = MetaGraphClient(access_token=token)
    data = await client.post(
        f"/{ig_user_id}/media_publish",
        data={"creation_id": creation_id},
    )
    return str(data["id"])


async def refresh_long_lived_token(token: str) -> dict[str, Any]:
    """
    Refresh a long-lived Instagram user token before it expires (60-day TTL).
    The token must be at least 24 hours old and not yet expired.
    Returns dict with: access_token, token_type, expires_in (seconds).
    """
    import httpx

    params = {
        "grant_type": "ig_refresh_token",
        "access_token": token,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(
            "https://graph.instagram.com/refresh_access_token",
            params=params,
        )
    response.raise_for_status()
    return response.json()  # type: ignore[no-any-return]


async def get_user_media(
    ig_user_id: str,
    token: str,
    limit: int = 12,
) -> list[dict[str, Any]]:
    """
    Fetch the most recent media items from an Instagram Business Account.
    Returns a list of media objects with public fields.
    """
    client = MetaGraphClient(access_token=token)
    data = await client.get(
        f"/{ig_user_id}/media",
        params={
            "fields": (
                "id,media_type,media_url,thumbnail_url,"
                "permalink,timestamp,like_count,comments_count,caption"
            ),
            "limit": str(limit),
        },
    )
    return data.get("data", [])  # type: ignore[no-any-return]


async def get_media_insights(media_id: str, token: str) -> dict[str, Any]:
    """
    Fetch insights for a single Instagram media object.
    Only available for Business/Creator accounts.
    Metrics: impressions, reach, saved, video_views (for videos/reels).
    """
    client = MetaGraphClient(access_token=token)
    return await client.get(
        f"/{media_id}/insights",
        params={"metric": "impressions,reach,saved"},
    )
