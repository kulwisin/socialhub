from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.content_file_repository import ContentFileRepository
from app.repositories.content_folder_repository import ContentFolderRepository
from app.schemas.content_file import ContentFileResponse
from app.schemas.content_folder import (
    ContentFolderCreate,
    ContentFolderResponse,
    ContentFolderUpdate,
)
from app.services.content_library_service import ContentLibraryService

router = APIRouter(prefix="/content", tags=["content"])


def _svc(db: AsyncSession = Depends(get_db)) -> ContentLibraryService:
    return ContentLibraryService(
        folder_repo=ContentFolderRepository(db),
        file_repo=ContentFileRepository(db),
    )


# ── folders ────────────────────────────────────────────────────────────────

@router.post(
    "/folders",
    response_model=ContentFolderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_folder(
    body: ContentFolderCreate,
    svc: ContentLibraryService = Depends(_svc),
) -> ContentFolderResponse:
    """Register a new content folder to watch."""
    return await svc.add_folder(body)


@router.get("/folders", response_model=list[ContentFolderResponse])
async def list_folders(
    svc: ContentLibraryService = Depends(_svc),
) -> list[ContentFolderResponse]:
    """List all active content folders."""
    return await svc.list_folders()


@router.get("/folders/{folder_id}", response_model=ContentFolderResponse)
async def get_folder(
    folder_id: uuid.UUID,
    svc: ContentLibraryService = Depends(_svc),
) -> ContentFolderResponse:
    return await svc.get_folder(folder_id)


@router.patch("/folders/{folder_id}", response_model=ContentFolderResponse)
async def update_folder(
    folder_id: uuid.UUID,
    body: ContentFolderUpdate,
    svc: ContentLibraryService = Depends(_svc),
) -> ContentFolderResponse:
    return await svc.update_folder(folder_id, body)


@router.delete("/folders/{folder_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_folder(
    folder_id: uuid.UUID,
    svc: ContentLibraryService = Depends(_svc),
) -> None:
    await svc.delete_folder(folder_id)


@router.post("/folders/{folder_id}/scan", response_model=dict)
async def scan_folder(
    folder_id: uuid.UUID,
    svc: ContentLibraryService = Depends(_svc),
) -> dict:
    """Scan a folder and upsert content_files for any video/audio found."""
    return await svc.scan_folder(folder_id)


# ── files ──────────────────────────────────────────────────────────────────

@router.get("/files", response_model=list[ContentFileResponse])
async def list_files(
    folder_id: uuid.UUID | None = None,
    status: str | None = None,
    skip: int = 0,
    limit: int = 50,
    svc: ContentLibraryService = Depends(_svc),
) -> list[ContentFileResponse]:
    """List content files, optionally filtered by folder or status."""
    return await svc.list_files(folder_id=folder_id, status=status, skip=skip, limit=limit)


@router.get("/files/{file_id}", response_model=ContentFileResponse)
async def get_file(
    file_id: uuid.UUID,
    svc: ContentLibraryService = Depends(_svc),
) -> ContentFileResponse:
    return await svc.get_file(file_id)
