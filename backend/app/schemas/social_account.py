from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SocialAccountResponse(BaseModel):
    """Public representation of a connected social account (no encrypted fields)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
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


class SocialAccountCreate(BaseModel):
    """Fields required to connect a new social account."""

    platform: str
    platform_user_id: str
    username: str
    display_name: str | None = None
    profile_image_url: str | None = None
    # Plaintext token — will be encrypted before storage
    access_token: str
    refresh_token: str | None = None
    token_expires_at: datetime | None = None
    facebook_page_id: str | None = None
    instagram_business_id: str | None = None
