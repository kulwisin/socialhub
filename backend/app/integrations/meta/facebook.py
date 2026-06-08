from __future__ import annotations

import httpx

from app.integrations.meta.client import MetaGraphClient

_TOKEN_URL = "https://graph.facebook.com/oauth/access_token"


async def get_page_long_lived_token(
    page_token: str,
    app_id: str,
    app_secret: str,
) -> str:
    """
    Exchange a page access token for one that never expires.
    Uses the Page token + app credentials to request an extended token.
    Returns the new long-lived page access token string.
    """
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": page_token,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(_TOKEN_URL, params=params)
    response.raise_for_status()
    data = response.json()
    return str(data["access_token"])


async def publish_video_to_page(
    page_id: str,
    page_token: str,
    video_path: str,
    description: str,
) -> str:
    """
    Upload a video file to a Facebook Page and return the resulting post_id.
    Uses multipart upload so the file is streamed from disk.
    """
    client = MetaGraphClient(access_token=page_token)
    with open(video_path, "rb") as fh:
        result = await client.post_multipart(
            f"/{page_id}/videos",
            files={"source": (video_path.split("/")[-1], fh, "video/mp4")},
            data={"description": description, "published": "true"},
        )
    # Graph API returns {"id": "<post_id>"} on success.
    return str(result["id"])
