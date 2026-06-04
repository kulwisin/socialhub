from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.db.session import get_db
from app.repositories.activity_log_repository import ActivityLogRepository
from app.repositories.post_repository import PostRepository
from app.repositories.social_account_repository import SocialAccountRepository
from app.repositories.upload_repository import UploadRepository
from app.schemas.post import PostResponse, PublishRequest, PublishResponse
from app.services.publisher_service import PublisherService

router = APIRouter(prefix="/posts", tags=["posts"])


def _make_publisher(db: AsyncSession) -> PublisherService:
    return PublisherService(
        upload_repo=UploadRepository(db),
        social_account_repo=SocialAccountRepository(db),
        post_repo=PostRepository(db),
        log_repo=ActivityLogRepository(db),
    )


@router.post(
    "/publish",
    response_model=PublishResponse,
    status_code=status.HTTP_200_OK,
)
async def publish(
    body: PublishRequest,
    db: AsyncSession = Depends(get_db),
) -> PublishResponse:
    """Publish an upload to one or more social accounts."""
    return await _make_publisher(db).publish(body)


@router.get("", response_model=list[PostResponse])
async def list_posts(
    limit: int = 20,
    status_filter: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[PostResponse]:
    """List recent posts, optionally filtered by status."""
    repo = PostRepository(db)
    posts = await repo.list_recent(limit=limit, status_filter=status_filter)
    return [PostResponse.model_validate(p) for p in posts]


@router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> PostResponse:
    repo = PostRepository(db)
    post = await repo.get(post_id)
    if post is None:
        raise NotFoundError(f"Post {post_id} not found.")
    return PostResponse.model_validate(post)
