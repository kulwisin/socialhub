from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PublishRequest(BaseModel):
    """Request body to trigger a publish operation."""

    upload_id: uuid.UUID
    account_ids: list[uuid.UUID] = Field(..., min_length=1)
    caption: str | None = None


class PostResponse(BaseModel):
    """Representation of a single publish job (one account × one upload)."""

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


class PublishResponse(BaseModel):
    """Aggregate result of a publish operation across multiple accounts."""

    posts: list[PostResponse]
    succeeded: int
    failed: int
