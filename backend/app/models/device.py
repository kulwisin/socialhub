from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import BaseModel


class Device(BaseModel):
    """A named container that holds one or more social accounts."""

    __tablename__ = "devices"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Arbitrary key/value metadata (icon color, notes, etc.)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    social_accounts: Mapped[list[SocialAccount]] = relationship(
        "SocialAccount",
        back_populates="device",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    def __repr__(self) -> str:
        return f"<Device id={self.id} name={self.name!r}>"
