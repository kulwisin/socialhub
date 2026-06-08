from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.repositories.ai_analysis_repository import AiAnalysisRepository
from app.repositories.content_file_repository import ContentFileRepository
from app.repositories.generated_content_repository import GeneratedContentRepository
from app.schemas.ai_analysis import AiAnalysisResponse
from app.schemas.generated_content import GeneratedContentResponse
from app.services.ai_analysis_service import AiAnalysisService
from app.services.generated_content_service import GeneratedContentService

router = APIRouter(prefix="/content", tags=["content-ai"])


def _analysis_svc(db: AsyncSession = Depends(get_db)) -> AiAnalysisService:
    return AiAnalysisService(
        file_repo=ContentFileRepository(db),
        analysis_repo=AiAnalysisRepository(db),
    )


def _gen_svc(db: AsyncSession = Depends(get_db)) -> GeneratedContentService:
    return GeneratedContentService(
        file_repo=ContentFileRepository(db),
        analysis_repo=AiAnalysisRepository(db),
        gen_repo=GeneratedContentRepository(db),
    )


@router.post("/files/{file_id}/analyze", response_model=AiAnalysisResponse)
async def analyze_file(
    file_id: uuid.UUID,
    svc: AiAnalysisService = Depends(_analysis_svc),
) -> AiAnalysisResponse:
    """Run Claude AI analysis on a content file (video or audio)."""
    return await svc.analyze_file(file_id)


@router.get("/files/{file_id}/analysis", response_model=AiAnalysisResponse)
async def get_analysis(
    file_id: uuid.UUID,
    svc: AiAnalysisService = Depends(_analysis_svc),
) -> AiAnalysisResponse:
    """Get the stored AI analysis for a file."""
    return await svc.get_analysis(file_id)


@router.post("/files/{file_id}/generate", response_model=list[GeneratedContentResponse])
async def generate_copy(
    file_id: uuid.UUID,
    platforms: Annotated[list[str] | None, Body(embed=True)] = None,
    svc: GeneratedContentService = Depends(_gen_svc),
) -> list[GeneratedContentResponse]:
    """Generate platform-optimized captions, hooks, and CTAs using Claude."""
    return await svc.generate_for_file(file_id, platforms=platforms)


@router.get("/files/{file_id}/generated", response_model=list[GeneratedContentResponse])
async def list_generated(
    file_id: uuid.UUID,
    svc: GeneratedContentService = Depends(_gen_svc),
) -> list[GeneratedContentResponse]:
    """List all generated platform copy for a file."""
    return await svc.list_generated(file_id)
