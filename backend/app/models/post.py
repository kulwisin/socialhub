from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

POST_STATUS_VALUES = ("queued", "publishing", "published", "failed")


class Post(BaseModel):
    """
    A publishing job: one Upload → one SocialAccount.
    One upload published to 3 accounts = 3 Post rows.
    """

    __tablename__ = "posts"
    __table_args__ = (
        CheckConstraint(f"status IN {POST_STATUS_VALUES}", name="chk_posts_status"),
    )

    upload_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("uploads.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    social_account_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("social_accounts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Caption can be overridden per-post (different caption per platform)
    caption: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Publishing state
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="queued", index=True)
    # ID returned by the platform after successful publish
    platform_post_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    retry_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    upload: Mapped[Upload] = relationship("Upload", back_populates="posts")
    social_account: Mapped[SocialAccount] = relationship(
        "SocialAccount", back_populates="posts"
    )

    def __repr__(self) -> str:
        return f"<Post id={self.id} status={self.status!r}>"
