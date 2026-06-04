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

# Extend when adding new platforms
PLATFORM_VALUES = ("instagram", "facebook", "tiktok")


class SocialAccount(BaseModel):
    """
    A social media account connected to a Device.
    Access tokens are stored Fernet-encrypted — never in plaintext.
    """

    __tablename__ = "social_accounts"
    __table_args__ = (
        UniqueConstraint("device_id", "platform", name="uq_social_accounts_device_platform"),
        CheckConstraint(
            f"platform IN {PLATFORM_VALUES}",
            name="chk_social_accounts_platform",
        ),
    )

    device_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("devices.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    platform: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Platform-returned identity
    platform_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_image_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    biography: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Stats (cached from last sync)
    followers_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    following_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    media_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Encrypted token storage — Fernet(ENCRYPTION_KEY)
    access_token_enc: Mapped[str] = mapped_column(Text, nullable=False)
    # Long-lived token or refresh token depending on platform
    refresh_token_enc: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    # Scopes granted during OAuth (stored for display and validation)
    scopes: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Linked Facebook Page ID (needed for Instagram Graph API publishing)
    facebook_page_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Instagram Business Account ID (ig_user_id returned by Graph API)
    instagram_business_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    device: Mapped[Device] = relationship("Device", back_populates="social_accounts")
    posts: Mapped[list[Post]] = relationship(
        "Post", back_populates="social_account", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<SocialAccount {self.platform}:{self.username}>"
