from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.post import Post
from app.models.upload import Upload
from app.repositories.base import BaseRepository


class PostRepository(BaseRepository[Post]):
    model = Post

    async def list_by_user(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Post]:
        """Return paginated posts for a user (via uploads.user_id), newest first."""
        stmt = (
            select(Post)
            .join(Upload, Post.upload_id == Upload.id)
            .where(Upload.user_id == user_id)
            .order_by(Post.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_upload(self, upload_id: uuid.UUID) -> list[Post]:
        """Return all posts associated with a given upload, newest first."""
        stmt = (
            select(Post)
            .where(Post.upload_id == upload_id)
            .order_by(Post.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
