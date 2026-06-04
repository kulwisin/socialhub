from __future__ import annotations

import logging
import mimetypes
import uuid
from datetime import datetime, timezone
from pathlib import Path

import aiofiles
from fastapi import UploadFile
from PIL import Image, UnidentifiedImageError

from app.core.config import settings
from app.core.exceptions import MediaProcessingError, NotFoundError
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.upload import UploadResponse

logger = logging.getLogger(__name__)


class UploadService:
    def __init__(
        self,
        upload_repo: UploadRepository,
        log_repo: ActivityLogRepository,
    ) -> None:
        self.upload_repo = upload_repo
        self.log_repo = log_repo

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _media_dir(self) -> Path:
        return Path(settings.MEDIA_DIR)

    def _build_file_path(self, ext: str) -> tuple[Path, str]:
        """
        Return (absolute_path, relative_path_str) for a new upload.
        relative_path is like "2026/06/04/<uuid>.mp4".
        """
        now = datetime.now(tz=timezone.utc)
        rel = Path(now.strftime("%Y/%m/%d")) / f"{uuid.uuid4()}{ext}"
        abs_path = self._media_dir() / rel
        abs_path.parent.mkdir(parents=True, exist_ok=True)
        return abs_path, str(rel)

    def _detect_media_type(self, mime: str | None) -> str:
        if mime and mime.startswith("image/"):
            return "image"
        return "video"

    async def _generate_thumbnail(self, source: Path, media_type: str) -> str | None:
        """
        For images: save a 320×320 thumbnail.
        For videos: skip (would need ffmpeg; just return None).
        """
        if media_type != "image":
            return None
        try:
            thumb_rel = str(source.parent.relative_to(self._media_dir()) / f"thumb_{source.name}")
            thumb_abs = self._media_dir() / thumb_rel
            with Image.open(source) as img:
                img.thumbnail((320, 320))
                img.save(thumb_abs)
            return thumb_rel
        except (UnidentifiedImageError, OSError) as exc:
            logger.warning("Thumbnail generation failed for %s: %s", source, exc)
            return None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def save_upload(
        self, file: UploadFile, caption: str | None = None
    ) -> UploadResponse:
        """
        Persist an uploaded file to disk, create the DB record, and return it.
        Raises MediaProcessingError if the file exceeds the size limit.
        """
        original_filename = file.filename or "upload"
        suffix = Path(original_filename).suffix.lower() or ""
        mime_type = file.content_type or mimetypes.guess_type(original_filename)[0]

        abs_path, rel_path = self._build_file_path(suffix)

        # Stream file to disk, checking size.
        total_bytes = 0
        upload_id = uuid.uuid4()

        try:
            async with aiofiles.open(abs_path, "wb") as out:
                while True:
                    chunk = await file.read(1024 * 256)  # 256 KB chunks
                    if not chunk:
                        break
                    total_bytes += len(chunk)
                    if total_bytes > settings.MAX_UPLOAD_BYTES:
                        # Clean up partial file before raising.
                        abs_path.unlink(missing_ok=True)
                        raise MediaProcessingError(
                            f"File exceeds maximum allowed size of "
                            f"{settings.MAX_UPLOAD_BYTES // (1024 * 1024)} MB."
                        )
                    await out.write(chunk)
        except MediaProcessingError:
            raise
        except OSError as exc:
            logger.exception("Failed to write upload file %s", abs_path)
            raise MediaProcessingError(f"Failed to save file: {exc}") from exc

        media_type = self._detect_media_type(mime_type)
        thumbnail_path = await self._generate_thumbnail(abs_path, media_type)

        try:
            upload = await self.upload_repo.create(
                {
                    "id": upload_id,
                    "original_filename": original_filename,
                    "file_path": rel_path,
                    "file_size_bytes": total_bytes,
                    "mime_type": mime_type,
                    "thumbnail_path": thumbnail_path,
                    "media_type": media_type,
                    "caption": caption,
                    "status": "ready",
                }
            )
        except Exception as exc:
            abs_path.unlink(missing_ok=True)
            logger.exception("DB error saving upload record")
            raise MediaProcessingError(f"Failed to save upload record: {exc}") from exc

        await self.log_repo.log(
            event_type="upload.created",
            resource_type="upload",
            resource_id=upload.id,
            description=f"File '{original_filename}' uploaded ({total_bytes} bytes).",
            metadata={"mime_type": mime_type, "media_type": media_type},
        )

        return UploadResponse.model_validate(upload)

    async def list_uploads(self, skip: int = 0, limit: int = 20) -> list[UploadResponse]:
        uploads = await self.upload_repo.list(skip=skip, limit=limit)
        return [UploadResponse.model_validate(u) for u in uploads]

    async def get_upload(self, id: uuid.UUID) -> UploadResponse:
        upload = await self.upload_repo.get(id)
        if upload is None:
            raise NotFoundError(f"Upload {id} not found.")
        return UploadResponse.model_validate(upload)

    async def delete_upload(self, id: uuid.UUID) -> None:
        upload = await self.upload_repo.get(id)
        if upload is None:
            raise NotFoundError(f"Upload {id} not found.")

        # Remove file from disk.
        abs_path = self._media_dir() / upload.file_path
        abs_path.unlink(missing_ok=True)

        # Remove thumbnail if present.
        if upload.thumbnail_path:
            thumb_abs = self._media_dir() / upload.thumbnail_path
            thumb_abs.unlink(missing_ok=True)

        await self.upload_repo.delete(id)
        await self.log_repo.log(
            event_type="upload.deleted",
            resource_type="upload",
            resource_id=id,
            description=f"Upload '{upload.original_filename}' deleted.",
        )
