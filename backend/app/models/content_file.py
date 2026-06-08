from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, CheckConstraint, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

FILE_TYPE_VALUES = ("video", "audio")
CONTENT_STATUS_VALUES = ("pending", "analyzing", "analyzed", "matched", "queued", "posted", "failed")


class ContentFile(BaseModel):
    __tablename__ = "content_files"
    __table_args__ = (
        CheckConstraint(f"file_type IN {FILE_TYPE_VALUES}", name="chk_content_files_type"),
        CheckConstraint(f"status IN {CONTENT_STATUS_VALUES}", name="chk_content_files_status"),
    )

    folder_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("content_folders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    thumbnail_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="pending", index=True
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    folder: Mapped[ContentFolder] = relationship("ContentFolder", back_populates="files")
    ai_analysis: Mapped[AiAnalysis | None] = relationship(
        "AiAnalysis", back_populates="content_file", uselist=False,
        cascade="all, delete-orphan"
    )
    generated_content: Mapped[list[GeneratedContent]] = relationship(
        "GeneratedContent", back_populates="content_file", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<ContentFile id={self.id} filename={self.filename!r} type={self.file_type!r}>"
