from __future__ import annotations

from sqlalchemy import select

from app.models.content_folder import ContentFolder
from app.repositories.base import BaseRepository


class ContentFolderRepository(BaseRepository[ContentFolder]):
    model = ContentFolder

    async def get_by_path(self, path: str) -> ContentFolder | None:
        stmt = select(ContentFolder).where(ContentFolder.path == path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_active(self) -> list[ContentFolder]:
        stmt = (
            select(ContentFolder)
            .where(ContentFolder.is_active.is_(True))
            .order_by(ContentFolder.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
