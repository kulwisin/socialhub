from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.endpoints.activity_logs import router as activity_router
from app.api.v1.endpoints.admin import router as admin_router
from app.api.v1.endpoints.content import router as content_router
from app.api.v1.endpoints.content_ai import router as content_ai_router
from app.api.v1.endpoints.devices import router as devices_router
from app.api.v1.endpoints.meta_oauth import router as meta_oauth_router
from app.api.v1.endpoints.posts import router as posts_router
from app.api.v1.endpoints.social_accounts import router as social_accounts_router
from app.api.v1.endpoints.uploads import router as uploads_router

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(devices_router)
api_router.include_router(social_accounts_router)
api_router.include_router(uploads_router)
api_router.include_router(posts_router)
api_router.include_router(activity_router)
api_router.include_router(meta_oauth_router)
api_router.include_router(admin_router)
api_router.include_router(content_router)
api_router.include_router(content_ai_router)
