from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SocialAccountSummary(BaseModel):
    """Minimal social account info embedded in other responses."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    platform: str
    username: str
    display_name: str | None
    profile_image_url: str | None
    is_active: bool


class SocialAccountResponse(BaseModel):
    """Full public representation of a social account (no encrypted tokens)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    device_id: uuid.UUID
    platform: str
    platform_user_id: str
    username: str
    display_name: str | None
    profile_image_url: str | None
    biography: str | None
    followers_count: int
    following_count: int
    media_count: int
    token_expires_at: datetime | None
    scopes: list[str] | None
    facebook_page_id: str | None
    instagram_business_id: str | None
    is_active: bool
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime


class SyncResponse(BaseModel):
    """Returned after syncing a social account's profile from the platform."""

    account: SocialAccountResponse
    synced: bool


class TokenRefreshResponse(BaseModel):
    """Returned after manually refreshing a platform token."""

    account_id: uuid.UUID
    platform: str
    refreshed: bool
    message: str


class InstagramMediaItem(BaseModel):
    """A single item from an Instagram account's media feed."""

    id: str
    media_type: str
    media_url: str | None = None
    thumbnail_url: str | None = None
    permalink: str | None = None
    timestamp: str | None = None
    like_count: int | None = None
    comments_count: int | None = None
    caption: str | None = None


class MediaFeedResponse(BaseModel):
    """Response from the account media feed endpoint."""

    account_id: uuid.UUID
    platform: str
    items: list[InstagramMediaItem]
