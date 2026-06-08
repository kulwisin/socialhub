from __future__ import annotations

import uuid

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class AiAnalysis(BaseModel):
    __tablename__ = "ai_analysis"

    content_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_files.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Scene / content analysis
    scenes: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    objects: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    activities: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    emotions: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    genre: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Summary fields
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    keywords: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    viral_potential_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Raw model response for debugging / re-processing
    raw_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    analyzed_at: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    model_used: Mapped[str | None] = mapped_column(String(100), nullable=True)

    content_file: Mapped[ContentFile] = relationship(
        "ContentFile", back_populates="ai_analysis"
    )

    def __repr__(self) -> str:
        return f"<AiAnalysis id={self.id} file={self.content_file_id} score={self.viral_potential_score}>"
