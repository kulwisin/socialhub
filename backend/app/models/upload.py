from __future__ import annotations

from sqlalchemy import BigInteger, CheckConstraint, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

MEDIA_TYPE_VALUES = ("video", "image")
UPLOAD_STATUS_VALUES = ("pending", "ready", "failed")


class Upload(BaseModel):
    """
    A media file uploaded by the user, ready to be published to one or more platforms.
    The file lives on disk at `file_path` (relative to MEDIA_DIR).
    """

    __tablename__ = "uploads"
    __table_args__ = (
        CheckConstraint(f"media_type IN {MEDIA_TYPE_VALUES}", name="chk_uploads_media_type"),
        CheckConstraint(f"status IN {UPLOAD_STATUS_VALUES}", name="chk_uploads_status"),
    )

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    # Path relative to MEDIA_DIR (e.g. "2026/06/04/<uuid>.mp4")
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # Thumbnail path (extracted from video on upload)
    thumbnail_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, default="video")

    # Caption to publish — can be customised per post before publishing
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing status
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    posts: Mapped[list[Post]] = relationship(
        "Post", back_populates="upload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Upload id={self.id} file={self.original_filename!r} status={self.status!r}>"
