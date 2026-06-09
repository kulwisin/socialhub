from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.schemas.social_account import SocialAccountCreate, SocialAccountResponse
from app.services.social_account_service import SocialAccountService

router = APIRouter(prefix="/accounts", tags=["accounts"])


def _get_service(db: AsyncSession) -> SocialAccountService:
    return SocialAccountService(
        account_repo=SocialAccountRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.get("", response_model=list[SocialAccountResponse])
async def list_accounts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[SocialAccountResponse]:
    """Return all social accounts connected to the authenticated user."""
    return await _get_service(db).list_accounts(current_user.id)


@router.post("", response_model=SocialAccountResponse, status_code=201)
async def add_account(
    body: SocialAccountCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> SocialAccountResponse:
    """Connect a new social media account."""
    return await _get_service(db).add_account(current_user.id, body)


@router.delete("/{account_id}", status_code=204)
async def remove_account(
    account_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> None:
    """Disconnect and delete a social account."""
    await _get_service(db).remove_account(current_user.id, account_id)


@router.patch("/{account_id}/toggle", response_model=SocialAccountResponse)
async def toggle_account(
    account_id: uuid.UUID,
    is_active: Annotated[bool, Body(embed=True)],
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> SocialAccountResponse:
    """Enable or disable a connected social account."""
    return await _get_service(db).toggle_active(current_user.id, account_id, is_active)
