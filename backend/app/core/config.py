from __future__ import annotations

import os
from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # App
    APP_ENV: str = "development"
    APP_DEBUG: bool = False
    APP_SECRET_KEY: str = Field(..., min_length=32)
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str = Field(...)

    # Encryption
    ENCRYPTION_KEY: str = Field(...)

    # Meta
    META_APP_ID: str = ""
    META_APP_SECRET: str = ""
    META_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/meta/callback"
    META_GRAPH_API_VERSION: str = "v21.0"

    # Personal tokens (personal-use, no OAuth flow needed)
    META_USER_ACCESS_TOKEN: str = ""
    META_PAGE_ACCESS_TOKEN: str = ""
    META_PAGE_ID: str = ""
    META_IG_ACCOUNT_ID: str = ""

    # TikTok
    TIKTOK_CLIENT_KEY: str = ""
    TIKTOK_CLIENT_SECRET: str = ""

    # Storage
    MEDIA_DIR: str = "/app/media"
    # 500 MB — Instagram Reels max is ~4 GB but keep it sane for MVP
    MAX_UPLOAD_BYTES: int = 500 * 1024 * 1024

    @field_validator("DATABASE_URL")
    @classmethod
    def ensure_asyncpg(cls, v: str) -> str:
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @property
    def is_production(self) -> bool:
        return self.APP_ENV == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings: Settings = get_settings()
