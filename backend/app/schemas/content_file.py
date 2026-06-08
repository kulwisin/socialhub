from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ContentFileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    folder_id: uuid.UUID
    filename: str
    file_path: str
    file_type: str
    file_size_bytes: int | None
    duration_seconds: float | None
    mime_type: str | None
    content_hash: str | None
    thumbnail_path: str | None
    status: str
    error_message: str | None
    created_at: datetime
    updated_at: datetime
