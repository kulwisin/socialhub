from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.device_repository import DeviceRepository
from app.schemas.device import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["devices"])


def _make_service(db: AsyncSession) -> DeviceService:
    return DeviceService(
        device_repo=DeviceRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.get("", response_model=list[DeviceResponse])
async def list_devices(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[DeviceResponse]:
    return await _make_service(db).list_devices(skip=skip, limit=limit)


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
async def create_device(
    body: DeviceCreate,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    return await _make_service(db).create_device(body)


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    return await _make_service(db).get_device(device_id)


@router.patch("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: uuid.UUID,
    body: DeviceUpdate,
    db: AsyncSession = Depends(get_db),
) -> DeviceResponse:
    return await _make_service(db).update_device(device_id, body)


@router.delete("/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_device(
    device_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    await _make_service(db).delete_device(device_id)
