from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.social_account import SocialAccountSummary


class DeviceCreate(BaseModel):
    """Payload to create a new device."""

    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None
    meta: dict[str, Any] = Field(default_factory=dict)


class DeviceUpdate(BaseModel):
    """Partial update payload for a device."""

    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = None
    meta: dict[str, Any] | None = None


class DeviceResponse(BaseModel):
    """Full device representation including connected social accounts."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str | None
    meta: dict[str, Any]
    social_accounts: list[SocialAccountSummary]
    created_at: datetime
    updated_at: datetime
