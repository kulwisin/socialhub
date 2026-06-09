from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.social_account import SocialAccount
from app.repositories.base import BaseRepository


class SocialAccountRepository(BaseRepository[SocialAccount]):
    model = SocialAccount

    async def list_by_user(self, user_id: uuid.UUID) -> list[SocialAccount]:
        """Return all accounts belonging to a user, newest first."""
        stmt = (
            select(SocialAccount)
            .where(SocialAccount.user_id == user_id)
            .order_by(SocialAccount.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_platform_user(
        self,
        user_id: uuid.UUID,
        platform: str,
        platform_user_id: str,
    ) -> SocialAccount | None:
        """Return the account matching user × platform × platform_user_id, or None."""
        stmt = select(SocialAccount).where(
            SocialAccount.user_id == user_id,
            SocialAccount.platform == platform,
            SocialAccount.platform_user_id == platform_user_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_for_publish(
        self, account_ids: list[uuid.UUID]
    ) -> list[SocialAccount]:
        """Return active social accounts matching the given UUIDs."""
        if not account_ids:
            return []
        stmt = select(SocialAccount).where(
            SocialAccount.id.in_(account_ids),
            SocialAccount.is_active.is_(True),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
