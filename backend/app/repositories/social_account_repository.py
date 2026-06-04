from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.social_account import SocialAccount
from app.repositories.base import BaseRepository


class SocialAccountRepository(BaseRepository[SocialAccount]):
    model = SocialAccount

    async def get_by_device_and_platform(
        self, device_id: uuid.UUID, platform: str
    ) -> SocialAccount | None:
        """Return the account for a specific device × platform combo."""
        stmt = select(SocialAccount).where(
            SocialAccount.device_id == device_id,
            SocialAccount.platform == platform,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_device(self, device_id: uuid.UUID) -> list[SocialAccount]:
        """Return all accounts belonging to a device, newest first."""
        stmt = (
            select(SocialAccount)
            .where(SocialAccount.device_id == device_id)
            .order_by(SocialAccount.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

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
