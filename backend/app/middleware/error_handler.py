from __future__ import annotations

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    ConflictError,
    MediaProcessingError,
    NotFoundError,
    PlatformAuthError,
    PlatformPublishError,
    SocialHubError,
    ValidationError,
)

logger = logging.getLogger(__name__)


def _json(status_code: int, **kwargs: object) -> JSONResponse:
    return JSONResponse(status_code=status_code, content=dict(kwargs))


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all domain exception → HTTP response mappings to the app."""

    @app.exception_handler(NotFoundError)
    async def handle_not_found(request: Request, exc: NotFoundError) -> JSONResponse:
        return _json(404, detail=str(exc))

    @app.exception_handler(ValidationError)
    async def handle_validation(request: Request, exc: ValidationError) -> JSONResponse:
        return _json(422, detail=str(exc))

    @app.exception_handler(ConflictError)
    async def handle_conflict(request: Request, exc: ConflictError) -> JSONResponse:
        return _json(409, detail=str(exc))

    @app.exception_handler(PlatformAuthError)
    async def handle_platform_auth(
        request: Request, exc: PlatformAuthError
    ) -> JSONResponse:
        # Try to extract platform from the exception message heuristically.
        message = str(exc)
        platform = "unknown"
        for name in ("instagram", "facebook", "tiktok", "meta"):
            if name in message.lower():
                platform = name
                break
        return _json(502, detail=message, platform=platform)

    @app.exception_handler(PlatformPublishError)
    async def handle_platform_publish(
        request: Request, exc: PlatformPublishError
    ) -> JSONResponse:
        return _json(502, detail=str(exc))

    @app.exception_handler(MediaProcessingError)
    async def handle_media_processing(
        request: Request, exc: MediaProcessingError
    ) -> JSONResponse:
        return _json(422, detail=str(exc))

    @app.exception_handler(SocialHubError)
    async def handle_base_error(request: Request, exc: SocialHubError) -> JSONResponse:
        logger.error("Unhandled domain error: %s", exc)
        return _json(500, detail="An internal error occurred.")

    @app.exception_handler(Exception)
    async def handle_generic(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception on %s %s", request.method, request.url)
        return _json(500, detail="An unexpected error occurred. Please try again.")
