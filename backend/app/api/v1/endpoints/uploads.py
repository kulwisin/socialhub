from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import UploadResponse
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _make_service(db: AsyncSession) -> UploadService:
    return UploadService(
        upload_repo=UploadRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    file: UploadFile = File(...),
    caption: str | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """Upload a media file (video or image)."""
    return await _make_service(db).save_upload(file, caption)


@router.get("", response_model=list[UploadResponse])
async def list_uploads(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
) -> list[UploadResponse]:
    """List recent uploads, newest first."""
    return await _make_service(db).list_uploads(skip=skip, limit=limit)


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    return await _make_service(db).get_upload(upload_id)


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    upload_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    await _make_service(db).delete_upload(upload_id)
