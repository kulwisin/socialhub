from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Lightweight health check for Docker / load balancer probes."""
    return {"status": "ok"}


@router.get("/api/v1/health")
async def api_health(db: Annotated[AsyncSession, Depends(get_db)]) -> dict[str, Any]:
    """Deep health check — verifies DB connectivity."""
    await db.execute(text("SELECT 1"))
    return {"status": "ok", "db": "ok", "version": "v1"}
