from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.post import Post
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    async def list_by_upload(self, upload_id: uuid.UUID) -> list[Post]:
        """Return all posts associated with a given upload."""
        stmt = (
            select(Post)
            .where(Post.upload_id == upload_id)
            .order_by(Post.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_recent(
        self, limit: int = 20, status_filter: str | None = None
    ) -> list[Post]:
        """Return recent posts, optionally filtered by status."""
        stmt = select(Post).order_by(Post.created_at.desc()).limit(limit)
        if status_filter is not None:
            stmt = stmt.where(Post.status == status_filter)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
