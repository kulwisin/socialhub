from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict

PLATFORM_VALUES = ("instagram", "tiktok", "youtube", "x", "threads", "snapchat")


class GeneratedContentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content_file_id: uuid.UUID
    platform: str
    caption: str | None
    hook: str | None
    cta: str | None
    title: str | None
    hashtags: list[str] | None
    created_at: datetime
    updated_at: datetime
