from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.health import router as health_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.middleware.error_handler import register_exception_handlers

logging.basicConfig(
    level=logging.DEBUG if settings.APP_DEBUG else logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Startup / shutdown lifecycle."""
    # Ensure media directory exists
    media_dir = Path(settings.MEDIA_DIR)
    media_dir.mkdir(parents=True, exist_ok=True)
    logger.info("MEDIA_DIR ready: %s", media_dir)

    # Refresh any Instagram tokens expiring within 10 days
    try:
        from app.db.session import AsyncSessionFactory
        from app.services.token_refresh_service import TokenRefreshService

        async with AsyncSessionFactory() as session:
            result = await TokenRefreshService(session).refresh_expiring_accounts()
            if result["refreshed"]:
                logger.info("Startup token refresh: %s", result)
    except Exception:
        # Never block startup for a token refresh failure
        logger.warning("Startup token refresh skipped (DB may not be ready yet)")

    yield
    logger.info("SocialHub API shutting down.")


def create_app() -> FastAPI:
    app = FastAPI(
        title="SocialHub API",
        version="0.1.0",
        description="Personal social media publishing dashboard.",
        lifespan=lifespan,
    )

    # --------------- CORS ---------------
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # --------------- Exception handlers ---------------
    register_exception_handlers(app)

    # --------------- Routers ---------------
    app.include_router(health_router)   # /health  and  /api/v1/health
    app.include_router(api_router)      # /api/v1/...

    # --------------- Static media ---------------
    # Mount after routers so /media/* doesn't shadow any API path.
    media_dir = Path(settings.MEDIA_DIR)
    media_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/media", StaticFiles(directory=str(media_dir)), name="media")

    return app


app = create_app()
