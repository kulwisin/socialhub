from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.models.device import Device
from app.repositories.base import BaseRepository


class DeviceRepository(BaseRepository[Device]):
    model = Device

    async def get_with_accounts(self, id: uuid.UUID) -> Device | None:
        """Load a device and eagerly join its social_accounts."""
        stmt = (
            select(Device)
            .options(selectinload(Device.social_accounts))
            .where(Device.id == id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
