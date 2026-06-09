from __future__ import annotations

import uuid

from sqlalchemy import or_, select

from app.models.upload import Upload
from app.repositories.base import BaseRepository


class UploadRepository(BaseRepository[Upload]):
    model = Upload

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Upload]:
        """Return paginated uploads for a user, newest first."""
        stmt = (
            select(Upload)
            .where(Upload.user_id == user_id)
            .order_by(Upload.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def search_by_user(
        self,
        user_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Upload]:
        """
        Case-insensitive ILIKE search on title, description, and original_filename
        for uploads belonging to the given user.
        """
        pattern = f"%{query}%"
        stmt = (
            select(Upload)
            .where(
                Upload.user_id == user_id,
                or_(
                    Upload.title.ilike(pattern),
                    Upload.description.ilike(pattern),
                    Upload.original_filename.ilike(pattern),
                ),
            )
            .order_by(Upload.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
