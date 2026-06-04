from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class ActivityLogResponse(BaseModel):
    """Public representation of an activity log entry."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    event_type: str
    resource_type: str | None
    resource_id: uuid.UUID | None
    description: str | None
    meta: dict[str, Any]
    created_at: datetime
    updated_at: datetime
