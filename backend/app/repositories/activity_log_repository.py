from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import select

from app.models.activity_log import ActivityLog
from app.repositories.base import BaseRepository


class ActivityLogRepository(BaseRepository[ActivityLog]):
    """Append-only repository — no update or delete operations."""

    model = ActivityLog

    async def log(
        self,
        event_type: str,
        resource_type: str | None = None,
        resource_id: uuid.UUID | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> ActivityLog:
        """Append a new audit entry to the activity log."""
        return await self.create(
            {
                "event_type": event_type,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "description": description,
                "meta": metadata or {},  # Python attr is "meta"; DB column is "metadata"
            }
        )

    async def list_recent(self, limit: int = 50) -> list[ActivityLog]:
        """Return the most recent activity log entries."""
        stmt = (
            select(ActivityLog)
            .order_by(ActivityLog.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    # Explicitly disable mutating base operations for this immutable log.
    async def update(self, id: uuid.UUID, data: dict[str, Any]) -> None:  # type: ignore[override]
        raise NotImplementedError("ActivityLog rows are immutable.")

    async def delete(self, id: uuid.UUID) -> bool:  # type: ignore[override]
        raise NotImplementedError("ActivityLog rows cannot be deleted.")
