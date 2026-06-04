from __future__ import annotations

from sqlalchemy import select

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    model = Upload

    async def list_recent(self, limit: int = 20) -> list[Upload]:
        """Return the most recently created uploads."""
        stmt = (
            select(Upload)
            .order_by(Upload.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
