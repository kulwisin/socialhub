from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AiAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    content_file_id: uuid.UUID
    scenes: list[str] | None
    objects: list[str] | None
    activities: list[str] | None
    emotions: list[str] | None
    genre: str | None
    category: str | None
    summary: str | None
    keywords: list[str] | None
    target_audience: str | None
    viral_potential_score: int | None
    model_used: str | None
    analyzed_at: datetime | None
    created_at: datetime
    updated_at: datetime
