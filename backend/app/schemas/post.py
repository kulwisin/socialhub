from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostResponse(BaseModel):
    """Representation of a single publish job (one account x one upload)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    upload_id: uuid.UUID
    social_account_id: uuid.UUID
    caption: str | None
    status: str
    platform_post_id: str | None
    error_message: str | None
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PublishRequest(BaseModel):
    """Request body to trigger a multi-account publish operation."""

    upload_id: uuid.UUID
    account_ids: list[uuid.UUID] = Field(..., min_length=1)
    title: str | None = None
    description: str | None = None
    hashtags: list[str] | None = None
    caption: str | None = None
