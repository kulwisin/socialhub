from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    ARRAY,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel

PLATFORM_VALUES = (
    "instagram",
    "youtube",
    "tiktok",
    "x",
    "threads",
    "snapchat",
)


class SocialAccount(BaseModel):
    """
    A social media account connected to a User.
    Access tokens are stored Fernet-encrypted — never in plaintext.
    Multiple accounts per platform are supported.
    """

    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint(
            "user_id", "platform", "platform_user_id",
            name="uq_social_accounts_user_platform_pid",
        ),
        CheckConstraint(
            f"platform IN {PLATFORM_VALUES}",
            name="chk_social_accounts_platform",
        ),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)

    followers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    following_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    media_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    scopes: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Meta-specific (Instagram Graph API needs the linked page ID)
    facebook_page_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    instagram_business_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    user: Mapped[User] = relationship("User", back_populates="social_accounts")
    posts: Mapped[list[Post]] = relationship(
        "Post", back_populates="social_account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SocialAccount {self.platform}:{self.username}>"
