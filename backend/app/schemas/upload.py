from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UploadResponse(BaseModel):
    """Full public representation of an uploaded media file."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    original_filename: str
    file_path: str
    file_size_bytes: int | None
    mime_type: str | None
    duration_seconds: float | None
    thumbnail_path: str | None
    media_type: str
    title: str | None
    description: str | None
    hashtags: list[str] | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime


class UploadUpdate(BaseModel):
    """Fields the user may edit after upload."""

    title: str | None = None
    description: str | None = None
    hashtags: list[str] | None = None
