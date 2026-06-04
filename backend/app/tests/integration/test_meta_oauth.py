"""
Tests for the Meta OAuth and social account endpoints.

The OAuth callback itself cannot be unit-tested without hitting Facebook,
so we test:
  - The authorize URL is well-formed
  - Account listing, sync, refresh-token, media endpoints return correct shapes
  - Token refresh service logic
  - Disconnect removes the account
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_authorize_url_requires_device_id(async_client: AsyncClient) -> None:
    """GET /auth/meta/authorize without device_id returns 422."""
    response = await async_client.get("/api/v1/auth/meta/authorize")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_authorize_url_shape(async_client: AsyncClient, sample_device) -> None:
    """GET /auth/meta/authorize returns a Facebook OAuth URL."""
    response = await async_client.get(
        f"/api/v1/auth/meta/authorize?device_id={sample_device.id}"
    )
    # META_APP_ID is empty in tests, so we just verify the structure
    assert response.status_code == 200
    data = response.json()
    assert "url" in data
    assert "facebook.com" in data["url"]
    assert str(sample_device.id) in data["url"]  # state param


@pytest.mark.asyncio
async def test_list_accounts_empty(async_client: AsyncClient, sample_device) -> None:
    """GET /devices/{id}/accounts returns empty list for a new device."""
    response = await async_client.get(
        f"/api/v1/devices/{sample_device.id}/accounts"
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_list_accounts_with_data(
    async_client: AsyncClient,
    sample_device,
    sample_social_account,
) -> None:
    """GET /devices/{id}/accounts returns connected accounts."""
    response = await async_client.get(
        f"/api/v1/devices/{sample_device.id}/accounts"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["platform"] == "instagram"
    assert data[0]["username"] == "test_user"
    # Encrypted tokens must never appear in the response
    assert "access_token_enc" not in data[0]
    assert "refresh_token_enc" not in data[0]


@pytest.mark.asyncio
async def test_disconnect_account(
    async_client: AsyncClient,
    sample_device,
    sample_social_account,
) -> None:
    """DELETE /accounts/{id} removes the account."""
    account_id = str(sample_social_account.id)

    delete_resp = await async_client.delete(f"/api/v1/accounts/{account_id}")
    assert delete_resp.status_code == 204

    # Verify it's gone
    list_resp = await async_client.get(
        f"/api/v1/devices/{sample_device.id}/accounts"
    )
    assert list_resp.status_code == 200
    assert list_resp.json() == []


@pytest.mark.asyncio
async def test_sync_account_instagram(
    async_client: AsyncClient,
    sample_social_account,
) -> None:
    """POST /accounts/{id}/sync calls Graph API and updates the profile."""
    mock_profile = {
        "username": "updated_user",
        "name": "Updated Name",
        "biography": "Test bio",
        "followers_count": 9999,
        "follows_count": 100,
        "media_count": 42,
        "profile_picture_url": "https://example.com/pic.jpg",
    }

    with patch(
        "app.services.instagram.service.ig_api.get_instagram_profile",
        new=AsyncMock(return_value=mock_profile),
    ):
        response = await async_client.post(
            f"/api/v1/accounts/{sample_social_account.id}/sync"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["synced"] is True
    assert data["account"]["username"] == "updated_user"
    assert data["account"]["followers_count"] == 9999
    assert "access_token_enc" not in data["account"]


@pytest.mark.asyncio
async def test_refresh_token_instagram(
    async_client: AsyncClient,
    sample_social_account,
) -> None:
    """POST /accounts/{id}/refresh-token refreshes an Instagram token."""
    mock_token_data = {
        "access_token": "new-long-lived-token-abc123",
        "token_type": "bearer",
        "expires_in": 5_184_000,
    }

    with patch(
        "app.services.instagram.service.ig_api.refresh_long_lived_token",
        new=AsyncMock(return_value=mock_token_data),
    ):
        response = await async_client.post(
            f"/api/v1/accounts/{sample_social_account.id}/refresh-token"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["refreshed"] is True
    assert "successfully" in data["message"]
    # New token must never leak into the response
    assert "new-long-lived-token-abc123" not in str(data)


@pytest.mark.asyncio
async def test_get_media_feed_instagram(
    async_client: AsyncClient,
    sample_social_account,
) -> None:
    """GET /accounts/{id}/media returns media items from Instagram."""
    mock_media = [
        {
            "id": "111",
            "media_type": "IMAGE",
            "media_url": "https://example.com/img1.jpg",
            "thumbnail_url": None,
            "permalink": "https://www.instagram.com/p/abc/",
            "timestamp": "2026-06-01T12:00:00+0000",
            "like_count": 42,
            "comments_count": 3,
            "caption": "Test caption",
        },
        {
            "id": "222",
            "media_type": "VIDEO",
            "media_url": "https://example.com/vid2.mp4",
            "thumbnail_url": "https://example.com/thumb2.jpg",
            "permalink": "https://www.instagram.com/p/def/",
            "timestamp": "2026-05-28T10:00:00+0000",
            "like_count": 100,
            "comments_count": 8,
            "caption": None,
        },
    ]

    with patch(
        "app.services.instagram.service.ig_api.get_user_media",
        new=AsyncMock(return_value=mock_media),
    ):
        response = await async_client.get(
            f"/api/v1/accounts/{sample_social_account.id}/media"
        )

    assert response.status_code == 200
    data = response.json()
    assert data["platform"] == "instagram"
    assert len(data["items"]) == 2
    assert data["items"][0]["id"] == "111"
    assert data["items"][1]["media_type"] == "VIDEO"


@pytest.mark.asyncio
async def test_get_media_feed_not_found(async_client: AsyncClient) -> None:
    """GET /accounts/{id}/media returns 404 for unknown account."""
    import uuid

    response = await async_client.get(f"/api/v1/accounts/{uuid.uuid4()}/media")
    assert response.status_code == 404
