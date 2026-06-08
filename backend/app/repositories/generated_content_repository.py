from __future__ import annotations

import uuid

from sqlalchemy import delete, select

from app.models.generated_content import GeneratedContent
from app.repositories.base import BaseRepository


class GeneratedContentRepository(BaseRepository[GeneratedContent]):
    model = GeneratedContent

    async def list_by_file(self, content_file_id: uuid.UUID) -> list[GeneratedContent]:
        stmt = (
            select(GeneratedContent)
            .where(GeneratedContent.content_file_id == content_file_id)
            .order_by(GeneratedContent.platform.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_file(self, content_file_id: uuid.UUID) -> int:
        stmt = delete(GeneratedContent).where(
            GeneratedContent.content_file_id == content_file_id
        )
        result = await self.session.execute(stmt)
        return result.rowcount
