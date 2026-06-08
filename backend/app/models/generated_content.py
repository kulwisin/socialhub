from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

PLATFORM_VALUES = ("instagram", "tiktok", "youtube", "x", "threads", "snapchat")


class GeneratedContent(BaseModel):
    __tablename__ = "generated_content"

    content_file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_files.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False)

    caption: Mapped[str | None] = mapped_column(Text, nullable=True)
    hook: Mapped[str | None] = mapped_column(Text, nullable=True)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    title: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)

    content_file: Mapped[ContentFile] = relationship(
        "ContentFile", back_populates="generated_content"
    )

    def __repr__(self) -> str:
        return f"<GeneratedContent id={self.id} platform={self.platform!r}>"
