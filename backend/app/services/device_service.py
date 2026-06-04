from __future__ import annotations

import uuid

from app.core.exceptions import NotFoundError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate


class DeviceService:
    def __init__(
        self,
        device_repo: DeviceRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self.device_repo = device_repo
        self.log_repo = log_repo

    async def list_devices(self, skip: int = 0, limit: int = 20) -> list[DeviceResponse]:
        """Return a paginated list of all devices."""
        devices = await self.device_repo.list(skip=skip, limit=limit)
        return [DeviceResponse.model_validate(d) for d in devices]

    async def get_device(self, id: uuid.UUID) -> DeviceResponse:
        """Return a single device by ID, with its social accounts."""
        device = await self.device_repo.get_with_accounts(id)
        if device is None:
            raise NotFoundError(f"Device {id} not found.")
        return DeviceResponse.model_validate(device)

    async def create_device(self, data: DeviceCreate) -> DeviceResponse:
        """Create a new device and return it."""
        device = await self.device_repo.create(data.model_dump())
        await self.log_repo.log(
            event_type="device.created",
            resource_type="device",
            resource_id=device.id,
            description=f"Device '{device.name}' created.",
        )
        return DeviceResponse.model_validate(device)

    async def update_device(self, id: uuid.UUID, data: DeviceUpdate) -> DeviceResponse:
        """Apply a partial update to an existing device."""
        existing = await self.device_repo.get(id)
        if existing is None:
            raise NotFoundError(f"Device {id} not found.")
        payload = data.model_dump(exclude_none=True)
        device = await self.device_repo.update(id, payload)
        await self.log_repo.log(
            event_type="device.updated",
            resource_type="device",
            resource_id=id,
            description=f"Device '{device.name}' updated.",
            metadata={"changed_fields": list(payload.keys())},
        )
        # Re-fetch with accounts to populate the relationship.
        return await self.get_device(id)

    async def delete_device(self, id: uuid.UUID) -> None:
        """Delete a device (cascade-deletes social accounts)."""
        device = await self.device_repo.get(id)
        if device is None:
            raise NotFoundError(f"Device {id} not found.")
        name = device.name
        deleted = await self.device_repo.delete(id)
        if deleted:
            await self.log_repo.log(
                event_type="device.deleted",
                resource_type="device",
                resource_id=id,
                description=f"Device '{name}' deleted.",
            )
