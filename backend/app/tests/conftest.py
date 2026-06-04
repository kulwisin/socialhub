from __future__ import annotations

import os
import uuid
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

# ---------------------------------------------------------------------------
# Set env vars BEFORE importing anything that reads them at module level.
# ---------------------------------------------------------------------------
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")
os.environ.setdefault("APP_SECRET_KEY", "test-secret-key-that-is-long-enough-32ch")
os.environ.setdefault(
    "ENCRYPTION_KEY",
    # A valid Fernet key (base64url, 32 bytes) — safe for tests only.
    "dGVzdC10ZXN0LXRlc3QtdGVzdC10ZXN0LXRlc3Q=",
)
os.environ.setdefault("MEDIA_DIR", "/tmp/socialhub_test_media")

from app.db.base import Base  # noqa: E402 — must be after env vars
from app.main import app  # noqa: E402
import app.models  # noqa: E402 — ensures all models are registered with Base.metadata

_ENGINE = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
_SESSION_FACTORY = async_sessionmaker(
    bind=_ENGINE,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def _create_tables() -> AsyncGenerator[None, None]:
    """Create all tables once for the test session."""
    async with _ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Provide a test DB session, rolling back after each test."""
    async with _SESSION_FACTORY() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture()
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an httpx AsyncClient pointed at the FastAPI test app.
    Override the get_db dependency to use the test session.
    """
    from app.db.session import get_db

    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
    app.dependency_overrides.clear()


@pytest_asyncio.fixture()
async def sample_device(db_session: AsyncSession):  # type: ignore[no-untyped-def]
    """A Device row persisted in the test database."""
    from app.models.device import Device

    device = Device(name="Test Device", description="Created by conftest", meta={})
    db_session.add(device)
    await db_session.flush()
    await db_session.refresh(device)
    return device


@pytest_asyncio.fixture()
async def sample_upload(db_session: AsyncSession, tmp_path: Path):  # type: ignore[no-untyped-def]
    """An Upload row pointing to a real temp file."""
    from app.models.upload import Upload

    media_dir = Path(os.environ["MEDIA_DIR"])
    media_dir.mkdir(parents=True, exist_ok=True)
    rel = "2026/01/01/test_video.mp4"
    abs_path = media_dir / rel
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_bytes(b"\x00" * 1024)  # dummy 1 KB "video"

    upload = Upload(
        original_filename="test_video.mp4",
        file_path=rel,
        file_size_bytes=1024,
        mime_type="video/mp4",
        media_type="video",
        status="ready",
    )
    db_session.add(upload)
    await db_session.flush()
    await db_session.refresh(upload)
    return upload


@pytest_asyncio.fixture()
async def sample_social_account(db_session: AsyncSession, sample_device):  # type: ignore[no-untyped-def]
    """A SocialAccount row linked to sample_device."""
    from app.core.crypto import encrypt
    from app.models.social_account import SocialAccount

    account = SocialAccount(
        device_id=sample_device.id,
        platform="instagram",
        platform_user_id="123456789",
        username="test_user",
        display_name="Test User",
        access_token_enc=encrypt("fake-access-token"),
        instagram_business_id="123456789",
        is_active=True,
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account
