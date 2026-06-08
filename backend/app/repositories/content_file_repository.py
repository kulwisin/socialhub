from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.content_file import ContentFile
from app.repositories.base import BaseRepository


class ContentFileRepository(BaseRepository[ContentFile]):
    model = ContentFile

    async def get_by_path(self, file_path: str) -> ContentFile | None:
        stmt = select(ContentFile).where(ContentFile.file_path == file_path)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_folder(
        self, folder_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> list[ContentFile]:
        stmt = (
            select(ContentFile)
            .where(ContentFile.folder_id == folder_id)
            .order_by(ContentFile.filename.asc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_status(
        self, status: str, skip: int = 0, limit: int = 50
    ) -> list[ContentFile]:
        stmt = (
            select(ContentFile)
            .where(ContentFile.status == status)
            .order_by(ContentFile.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_hash(self, content_hash: str) -> ContentFile | None:
        stmt = select(ContentFile).where(ContentFile.content_hash == content_hash)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
