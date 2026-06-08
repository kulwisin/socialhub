from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict, field_validator


class ContentFolderCreate(BaseModel):
    path: str
    label: str

    @field_validator("path")
    @classmethod
    def path_must_be_absolute(cls, v: str) -> str:
        if not v.startswith("/"):
            raise ValueError("path must be an absolute filesystem path")
        return v.rstrip("/")


class ContentFolderUpdate(BaseModel):
    label: str | None = None
    is_active: bool | None = None


class ContentFolderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    path: str
    label: str
    is_active: bool
    last_scanned_at: datetime | None
    created_at: datetime
    updated_at: datetime
