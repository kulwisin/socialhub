from __future__ import annotations

import logging
import mimetypes
import uuid
from pathlib import Path

import aiofiles
from fastapi import UploadFile

from app.core.config import settings
from app.core.exceptions import MediaProcessingError, NotFoundError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import UploadResponse, UploadUpdate

logger = logging.getLogger(__name__)

# MIME types accepted as video uploads
_VIDEO_MIMES = {
    "video/mp4",
    "video/quicktime",
    "video/x-msvideo",
    "video/webm",
    "video/x-matroska",
}
# MIME types accepted as image uploads
_IMAGE_MIMES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}
_ALLOWED_MIMES = _VIDEO_MIMES | _IMAGE_MIMES


class UploadService:
    def __init__(
        self,
        upload_repo: UploadRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self._uploads = upload_repo
        self._logs = log_repo

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _media_dir(self) -> Path:
        p = Path(settings.MEDIA_DIR)
        p.mkdir(parents=True, exist_ok=True)
        return p

    def _detect_media_type(self, mime: str) -> str:
        return "video" if mime in _VIDEO_MIMES else "image"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def save_upload(
        self,
        user_id: uuid.UUID,
        file: UploadFile,
        title: str | None = None,
        description: str | None = None,
        hashtags: list[str] | None = None,
    ) -> UploadResponse:
        """Stream a multipart file to disk and create an Upload record."""
        # Determine MIME type
        content_type = file.content_type or ""
        if not content_type:
            guessed, _ = mimetypes.guess_type(file.filename or "")
            content_type = guessed or "application/octet-stream"

        if content_type not in _ALLOWED_MIMES:
            raise MediaProcessingError(
                f"File type '{content_type}' is not allowed. "
                "Accepted: video/mp4, video/quicktime, video/webm, "
                "image/jpeg, image/png, image/gif, image/webp."
            )

        # Build a unique filename to avoid collisions
        ext = Path(file.filename or "upload").suffix or ""
        unique_name = f"{uuid.uuid4().hex}{ext}"
        dest_path = self._media_dir() / unique_name

        # Stream to disk
        total_bytes = 0
        try:
            async with aiofiles.open(dest_path, "wb") as out_file:
                while True:
                    chunk = await file.read(1024 * 1024)  # 1 MB chunks
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_UPLOAD_BYTES:
                        dest_path.unlink(missing_ok=True)
                        raise MediaProcessingError(
                            f"Upload exceeds maximum size of "
                            f"{settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
                        )
                    await out_file.write(chunk)
        except MediaProcessingError:
            raise
        except OSError as exc:
            dest_path.unlink(missing_ok=True)
            raise MediaProcessingError(f"Failed to save file: {exc}") from exc

        media_type = self._detect_media_type(content_type)

        upload = await self._uploads.create(
            {
                "user_id": user_id,
                "original_filename": file.filename or unique_name,
                "file_path": unique_name,
                "file_size_bytes": total_bytes,
                "mime_type": content_type,
                "media_type": media_type,
                "title": title,
                "description": description,
                "hashtags": hashtags or [],
                "status": "ready",
            }
        )
        await self._logs.log(
            event_type="upload.created",
            resource_type="upload",
            resource_id=upload.id,
            description=f"Uploaded {file.filename!r} ({total_bytes} bytes)",
            metadata={
                "filename": file.filename,
                "mime_type": content_type,
                "size_bytes": total_bytes,
            },
        )
        return UploadResponse.model_validate(upload)

    async def list_uploads(
        self,
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UploadResponse]:
        uploads = await self._uploads.list_by_user(user_id, skip=skip, limit=limit)
        return [UploadResponse.model_validate(u) for u in uploads]

    async def search_uploads(
        self,
        user_id: uuid.UUID,
        query: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UploadResponse]:
        uploads = await self._uploads.search_by_user(
            user_id, query=query, skip=skip, limit=limit
        )
        return [UploadResponse.model_validate(u) for u in uploads]

    async def get_upload(
        self,
        user_id: uuid.UUID,
        upload_id: uuid.UUID,
    ) -> UploadResponse:
        """Return an upload owned by the user, or raise NotFoundError."""
        upload = await self._uploads.get(upload_id)
        if upload is None or upload.user_id != user_id:
            raise NotFoundError(f"Upload {upload_id} not found.")
        return UploadResponse.model_validate(upload)

    async def update_upload(
        self,
        user_id: uuid.UUID,
        upload_id: uuid.UUID,
        data: UploadUpdate,
    ) -> UploadResponse:
        upload = await self._uploads.get(upload_id)
        if upload is None or upload.user_id != user_id:
            raise NotFoundError(f"Upload {upload_id} not found.")

        patch = data.model_dump(exclude_unset=True)
        updated = await self._uploads.update(upload_id, patch)
        if updated is None:
            raise NotFoundError(f"Upload {upload_id} not found.")
        return UploadResponse.model_validate(updated)

    async def delete_upload(
        self,
        user_id: uuid.UUID,
        upload_id: uuid.UUID,
    ) -> None:
        upload = await self._uploads.get(upload_id)
        if upload is None or upload.user_id != user_id:
            raise NotFoundError(f"Upload {upload_id} not found.")

        # Remove physical file
        file_path = self._media_dir() / upload.file_path
        file_path.unlink(missing_ok=True)

        await self._uploads.delete(upload_id)
        await self._logs.log(
            event_type="upload.deleted",
            resource_type="upload",
            resource_id=upload_id,
            description=f"Deleted upload {upload.original_filename!r}",
            metadata={"filename": upload.original_filename},
        )
