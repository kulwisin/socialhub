from __future__ import annotations

import hashlib
import logging
import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.repositories.content_file_repository import ContentFileRepository
from app.repositories.content_folder_repository import ContentFolderRepository
from app.schemas.content_file import ContentFileResponse
from app.schemas.content_folder import (
    ContentFolderCreate,
    ContentFolderResponse,
    ContentFolderUpdate,
)

logger = logging.getLogger(__name__)

_VIDEO_MIME_PREFIXES = ("video/",)
_AUDIO_MIME_PREFIXES = ("audio/",)
_SCANNABLE_SUFFIXES = {
    ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v",
    ".mp3", ".wav", ".aac", ".flac", ".m4a", ".ogg",
}


def _classify(path: Path) -> tuple[str, str | None]:
    """Return (file_type, mime_type) for the given path."""
    mime = mimetypes.guess_type(path.name)[0] or ""
    if mime.startswith("video/") or path.suffix.lower() in {
        ".mp4", ".mov", ".avi", ".mkv", ".webm", ".m4v"
    }:
        return "video", mime or None
    return "audio", mime or None


def _sha256(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while data := fh.read(chunk):
            h.update(data)
    return h.hexdigest()


class ContentLibraryService:
    def __init__(
        self,
        folder_repo: ContentFolderRepository,
        file_repo: ContentFileRepository,
    ) -> None:
        self.folder_repo = folder_repo
        self.file_repo = file_repo

    # ── folders ────────────────────────────────────────────────────────────

    async def add_folder(self, data: ContentFolderCreate) -> ContentFolderResponse:
        if not Path(data.path).is_dir():
            raise ValidationError(f"Path does not exist or is not a directory: {data.path}")
        existing = await self.folder_repo.get_by_path(data.path)
        if existing is not None:
            raise ConflictError(f"Folder already registered: {data.path}")
        folder = await self.folder_repo.create({"path": data.path, "label": data.label})
        return ContentFolderResponse.model_validate(folder)

    async def list_folders(self) -> list[ContentFolderResponse]:
        folders = await self.folder_repo.list_active()
        return [ContentFolderResponse.model_validate(f) for f in folders]

    async def get_folder(self, folder_id: uuid.UUID) -> ContentFolderResponse:
        folder = await self.folder_repo.get(folder_id)
        if folder is None:
            raise NotFoundError(f"Folder {folder_id} not found.")
        return ContentFolderResponse.model_validate(folder)

    async def update_folder(
        self, folder_id: uuid.UUID, data: ContentFolderUpdate
    ) -> ContentFolderResponse:
        folder = await self.folder_repo.update(
            folder_id, data.model_dump(exclude_none=True)
        )
        if folder is None:
            raise NotFoundError(f"Folder {folder_id} not found.")
        return ContentFolderResponse.model_validate(folder)

    async def delete_folder(self, folder_id: uuid.UUID) -> None:
        deleted = await self.folder_repo.delete(folder_id)
        if not deleted:
            raise NotFoundError(f"Folder {folder_id} not found.")

    # ── scanning ───────────────────────────────────────────────────────────

    async def scan_folder(self, folder_id: uuid.UUID) -> dict[str, int]:
        """
        Walk the folder on disk and upsert content_files rows.
        Returns a summary dict with counts: added, updated, skipped.
        """
        folder = await self.folder_repo.get(folder_id)
        if folder is None:
            raise NotFoundError(f"Folder {folder_id} not found.")

        root = Path(folder.path)
        if not root.is_dir():
            raise ValidationError(f"Folder path no longer exists: {folder.path}")

        added = updated = skipped = 0

        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in _SCANNABLE_SUFFIXES:
                continue

            file_type, mime_type = _classify(path)
            file_path_str = str(path)

            try:
                content_hash = _sha256(path)
                file_size = path.stat().st_size
            except OSError as exc:
                logger.warning("Skipping unreadable file %s: %s", path, exc)
                skipped += 1
                continue

            existing = await self.file_repo.get_by_path(file_path_str)

            if existing is None:
                await self.file_repo.create(
                    {
                        "folder_id": folder.id,
                        "filename": path.name,
                        "file_path": file_path_str,
                        "file_type": file_type,
                        "file_size_bytes": file_size,
                        "mime_type": mime_type,
                        "content_hash": content_hash,
                        "status": "pending",
                    }
                )
                added += 1
            else:
                if existing.content_hash != content_hash:
                    await self.file_repo.update(
                        existing.id,
                        {
                            "content_hash": content_hash,
                            "file_size_bytes": file_size,
                            "mime_type": mime_type,
                            "status": "pending",
                            "error_message": None,
                        },
                    )
                    updated += 1
                else:
                    skipped += 1

        await self.folder_repo.update(
            folder_id, {"last_scanned_at": datetime.now(tz=timezone.utc)}
        )

        return {"added": added, "updated": updated, "skipped": skipped}

    # ── files ──────────────────────────────────────────────────────────────

    async def list_files(
        self,
        folder_id: uuid.UUID | None = None,
        status: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[ContentFileResponse]:
        if folder_id is not None:
            files = await self.file_repo.list_by_folder(folder_id, skip=skip, limit=limit)
        elif status is not None:
            files = await self.file_repo.list_by_status(status, skip=skip, limit=limit)
        else:
            files = await self.file_repo.list(skip=skip, limit=limit)
        return [ContentFileResponse.model_validate(f) for f in files]

    async def get_file(self, file_id: uuid.UUID) -> ContentFileResponse:
        f = await self.file_repo.get(file_id)
        if f is None:
            raise NotFoundError(f"ContentFile {file_id} not found.")
        return ContentFileResponse.model_validate(f)
