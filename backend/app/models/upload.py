from __future__ import annotations

import uuid

from sqlalchemy import ARRAY, BigInteger, CheckConstraint, Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

MEDIA_TYPE_VALUES = ("video", "image")
UPLOAD_STATUS_VALUES = ("pending", "ready", "failed")


class Upload(BaseModel):
    """
    A media file uploaded by the user. Can be published to multiple accounts.
    file_path is relative to MEDIA_DIR.
    """

    __tablename__ = "uploads"
    __table_args__ = (
        CheckConstraint(f"media_type IN {MEDIA_TYPE_VALUES}", name="chk_uploads_media_type"),
        CheckConstraint(f"status IN {UPLOAD_STATUS_VALUES}", name="chk_uploads_status"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    original_filename: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    thumbnail_path: Mapped[str | None] = mapped_column(Text, nullable=True)
    media_type: Mapped[str] = mapped_column(String(20), nullable=False, default="video")

    # Content metadata — entered manually by the user
    title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    hashtags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending", index=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    user: Mapped[User] = relationship("User", back_populates="uploads")
    posts: Mapped[list[Post]] = relationship(
        "Post", back_populates="upload", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Upload id={self.id} file={self.original_filename!r} status={self.status!r}>"
