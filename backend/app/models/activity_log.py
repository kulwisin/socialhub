from __future__ import annotations

import uuid

from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import BaseModel


class ActivityLog(BaseModel):
    """
    Immutable audit trail.
    Appended by services — never updated or deleted.
    """

    __tablename__ = "activity_logs"
    __table_args__ = (
        Index("ix_activity_logs_resource", "resource_type", "resource_id"),
    )

    # e.g. "device.created", "post.published", "account.connected"
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    # e.g. "device", "post", "social_account"
    resource_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    # Platform name, error details, post IDs, etc.
    # NOTE: "metadata" is reserved by SQLAlchemy's DeclarativeBase; we use "meta" instead.
    meta: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)

    def __repr__(self) -> str:
        return f"<ActivityLog event={self.event_type!r}>"
