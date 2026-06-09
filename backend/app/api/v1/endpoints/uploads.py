from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import UploadResponse, UploadUpdate
from app.services.upload_service import UploadService

router = APIRouter(prefix="/uploads", tags=["uploads"])


def _make_service(db: AsyncSession) -> UploadService:
    return UploadService(
        upload_repo=UploadRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.post("", response_model=UploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_file(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    description: str | None = Form(default=None),
    hashtags: str | None = Form(default=None),
) -> UploadResponse:
    """Upload a media file (video or image). hashtags is a comma-separated string."""
    tag_list: list[str] | None = None
    if hashtags:
        tag_list = [h.strip().lstrip("#") for h in hashtags.split(",") if h.strip()]
    return await _make_service(db).save_upload(
        user_id=current_user.id,
        file=file,
        title=title,
        description=description,
        hashtags=tag_list,
    )


@router.get("/search", response_model=list[UploadResponse])
async def search_uploads(
    q: str,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
) -> list[UploadResponse]:
    """Full-text search on title, description, and filename."""
    return await _make_service(db).search_uploads(
        current_user.id, query=q, skip=skip, limit=limit
    )


@router.get("", response_model=list[UploadResponse])
async def list_uploads(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
) -> list[UploadResponse]:
    """List uploads belonging to the authenticated user, newest first."""
    return await _make_service(db).list_uploads(current_user.id, skip=skip, limit=limit)


@router.get("/{upload_id}", response_model=UploadResponse)
async def get_upload(
    upload_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """Retrieve a single upload by ID."""
    return await _make_service(db).get_upload(current_user.id, upload_id)


@router.patch("/{upload_id}", response_model=UploadResponse)
async def update_upload(
    upload_id: uuid.UUID,
    body: UploadUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> UploadResponse:
    """Update title, description, or hashtags on an upload."""
    return await _make_service(db).update_upload(current_user.id, upload_id, body)


@router.delete("/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_upload(
    upload_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete an upload and its file from disk."""
    await _make_service(db).delete_upload(current_user.id, upload_id)
