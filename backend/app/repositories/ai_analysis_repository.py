from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.ai_analysis import AiAnalysis
from app.repositories.base import BaseRepository


class AiAnalysisRepository(BaseRepository[AiAnalysis]):
    model = AiAnalysis

    async def get_by_file(self, content_file_id: uuid.UUID) -> AiAnalysis | None:
        stmt = select(AiAnalysis).where(AiAnalysis.content_file_id == content_file_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
