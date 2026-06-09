from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.auth import get_current_user
from app.db.session import get_db
from app.models.user import User
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.post_repository import PostRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.post import PostResponse, PublishRequest
from app.services.publish_service import PublishService

router = APIRouter(prefix="/posts", tags=["posts"])


def _make_service(db: AsyncSession) -> PublishService:
    return PublishService(
        upload_repo=UploadRepository(db),
        account_repo=SocialAccountRepository(db),
        post_repo=PostRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.post(
    "/publish",
    response_model=list[PostResponse],
    status_code=status.HTTP_200_OK,
)
async def publish(
    body: PublishRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    """Publish an upload to one or more social accounts."""
    return await _make_service(db).publish(current_user.id, body)


@router.get("", response_model=list[PostResponse])
async def list_posts(
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
) -> list[PostResponse]:
    """List posts for the authenticated user, newest first."""
    return await _make_service(db).list_posts(current_user.id, skip=skip, limit=limit)


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    """Retrieve a single post by ID."""
    return await _make_service(db).get_post(current_user.id, post_id)
