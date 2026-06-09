from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_service(db: AsyncSession) -> AuthService:
    return AuthService(
        user_repo=UserRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Create a new user account and return a JWT."""
    service = _get_service(db)
    return await service.register(
        email=body.email,
        password=body.password,
        name=body.name,
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    """Authenticate with email/password and return a JWT."""
    service = _get_service(db)
    return await service.login(email=body.email, password=body.password)
