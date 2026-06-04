from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-that-is-long-enough-32ch")
os.environ.setdefault("ENCRYPTION_KEY", "dGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3Q=")
os.environ.setdefault("MEDIA_DIR", "/tmp/socialhub_test_media")

from app.core.exceptions import NotFoundError
from app.schemas.device import DeviceCreate, DeviceUpdate
from app.services.device_service import DeviceService


def _make_fake_device(
    name: str = "My Device",
    description: str | None = None,
    id: uuid.UUID | None = None,
) -> MagicMock:
    device = MagicMock()
    device.id = id or uuid.uuid4()
    device.name = name
    device.description = description
    device.meta = {}
    device.social_accounts = []
    device.created_at = MagicMock()
    device.updated_at = MagicMock()
    return device


def _make_service() -> tuple[DeviceService, MagicMock, MagicMock]:
    device_repo = MagicMock()
    log_repo = MagicMock()
    log_repo.log = AsyncMock(return_value=MagicMock())
    svc = DeviceService(device_repo=device_repo, log_repo=log_repo)
    return svc, device_repo, log_repo


@pytest.mark.asyncio
async def test_create_device() -> None:
    svc, device_repo, log_repo = _make_service()
    fake = _make_fake_device(name="New Device")
    device_repo.create = AsyncMock(return_value=fake)

    result = await svc.create_device(DeviceCreate(name="New Device"))

    device_repo.create.assert_awaited_once()
    log_repo.log.assert_awaited_once()
    assert result.name == "New Device"
    assert result.id == fake.id


@pytest.mark.asyncio
async def test_get_device_found() -> None:
    svc, device_repo, _ = _make_service()
    device_id = uuid.uuid4()
    fake = _make_fake_device(name="Found Device", id=device_id)
    device_repo.get_with_accounts = AsyncMock(return_value=fake)

    result = await svc.get_device(device_id)

    device_repo.get_with_accounts.assert_awaited_once_with(device_id)
    assert result.id == device_id
    assert result.name == "Found Device"


@pytest.mark.asyncio
async def test_get_device_not_found() -> None:
    svc, device_repo, _ = _make_service()
    device_repo.get_with_accounts = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError, match="not found"):
        await svc.get_device(uuid.uuid4())


@pytest.mark.asyncio
async def test_update_device() -> None:
    svc, device_repo, log_repo = _make_service()
    device_id = uuid.uuid4()
    existing = _make_fake_device(name="Old Name", id=device_id)
    updated = _make_fake_device(name="New Name", id=device_id)

    device_repo.get = AsyncMock(return_value=existing)
    device_repo.update = AsyncMock(return_value=updated)
    # get_with_accounts called internally by update_device for re-fetch.
    device_repo.get_with_accounts = AsyncMock(return_value=updated)

    result = await svc.update_device(device_id, DeviceUpdate(name="New Name"))

    device_repo.update.assert_awaited_once()
    log_repo.log.assert_awaited_once()
    assert result.name == "New Name"


@pytest.mark.asyncio
async def test_update_device_not_found() -> None:
    svc, device_repo, _ = _make_service()
    device_repo.get = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await svc.update_device(uuid.uuid4(), DeviceUpdate(name="X"))


@pytest.mark.asyncio
async def test_delete_device() -> None:
    svc, device_repo, log_repo = _make_service()
    device_id = uuid.uuid4()
    existing = _make_fake_device(id=device_id)
    device_repo.get = AsyncMock(return_value=existing)
    device_repo.delete = AsyncMock(return_value=True)

    await svc.delete_device(device_id)

    device_repo.delete.assert_awaited_once_with(device_id)
    log_repo.log.assert_awaited_once()


@pytest.mark.asyncio
async def test_delete_device_not_found() -> None:
    svc, device_repo, _ = _make_service()
    device_repo.get = AsyncMock(return_value=None)

    with pytest.raises(NotFoundError):
        await svc.delete_device(uuid.uuid4())
