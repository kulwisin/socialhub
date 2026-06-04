from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.schemas.activity_log import ActivityLogResponse

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("", response_model=list[ActivityLogResponse])
async def list_activity(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[ActivityLogResponse]:
    """Return recent activity log entries, newest first."""
    repo = ActivityLogRepository(db)
    logs = await repo.list_recent(limit=limit)
    return [ActivityLogResponse.model_validate(entry) for entry in logs]
