from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Any

import anthropic

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.ai_analysis_repository import AiAnalysisRepository
from app.repositories.content_file_repository import ContentFileRepository
from app.repositories.generated_content_repository import GeneratedContentRepository
from app.schemas.generated_content import GeneratedContentResponse

logger = logging.getLogger(__name__)

MODEL = "claude-sonnet-4-6"

ALL_PLATFORMS = ["instagram", "tiktok", "youtube", "x", "threads", "snapchat"]

_COPY_PROMPT_TEMPLATE = """\
You are an expert social media copywriter specializing in viral content for music artists and creators.

Content details:
- Filename: {filename}
- Genre: {genre}
- Category: {category}
- Summary: {summary}
- Emotions: {emotions}
- Keywords: {keywords}
- Target audience: {target_audience}
- Viral potential score: {score}/100

Write platform-optimized copy for each of these platforms: {platforms}

Return a JSON array where each element has:
{{
  "platform": "<platform name>",
  "hook": "<attention-grabbing first line, max 15 words>",
  "caption": "<full post caption with natural flow>",
  "cta": "<call-to-action, max 10 words>",
  "title": "<short title for platforms that use it, or null>",
  "hashtags": ["list", "of", "10-20", "hashtags", "without", "#"]
}}

Platform guidelines:
- instagram: emoji-rich, 150-300 chars caption, strong hook, 15-20 hashtags
- tiktok: casual/conversational, trend-aware, short punchy caption, 5-10 hashtags
- youtube: longer caption ok (2-3 sentences), SEO-friendly title, 10-15 hashtags
- x: concise under 280 chars total including hashtags, 3-5 hashtags
- threads: conversational, no hashtag overload, 1-3 hashtags, feels personal
- snapchat: very short, hype-forward, 0-3 hashtags, casual tone

Return ONLY the JSON array, no markdown fences."""


def _parse_copy(raw: str) -> list[dict[str, Any]]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


class GeneratedContentService:
    def __init__(
        self,
        file_repo: ContentFileRepository,
        analysis_repo: AiAnalysisRepository,
        gen_repo: GeneratedContentRepository,
    ) -> None:
        self.file_repo = file_repo
        self.analysis_repo = analysis_repo
        self.gen_repo = gen_repo

    def _client(self) -> anthropic.Anthropic:
        if not settings.ANTHROPIC_API_KEY:
            raise ValidationError(
                "ANTHROPIC_API_KEY is not configured. Add it to .env."
            )
        return anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    async def generate_for_file(
        self,
        file_id: uuid.UUID,
        platforms: list[str] | None = None,
    ) -> list[GeneratedContentResponse]:
        """Generate platform copy for an analyzed file. Replaces any existing generated content."""
        content_file = await self.file_repo.get(file_id)
        if content_file is None:
            raise NotFoundError(f"ContentFile {file_id} not found.")

        analysis = await self.analysis_repo.get_by_file(file_id)
        if analysis is None:
            raise ValidationError(
                f"File {file_id} has not been analyzed yet. Run /analyze first."
            )

        target_platforms = platforms or ALL_PLATFORMS

        raw, items = await asyncio.get_event_loop().run_in_executor(
            None,
            self._run_claude,
            content_file,
            analysis,
            target_platforms,
        )

        # Replace old generated content for this file
        await self.gen_repo.delete_by_file(file_id)

        results = []
        for item in items:
            platform = item.get("platform", "").lower()
            if platform not in target_platforms:
                continue
            record = await self.gen_repo.create(
                {
                    "content_file_id": file_id,
                    "platform": platform,
                    "hook": item.get("hook"),
                    "caption": item.get("caption"),
                    "cta": item.get("cta"),
                    "title": item.get("title"),
                    "hashtags": item.get("hashtags") or [],
                }
            )
            results.append(GeneratedContentResponse.model_validate(record))

        await self.file_repo.update(file_id, {"status": "matched"})
        return results

    def _run_claude(
        self, content_file, analysis, platforms: list[str]
    ) -> tuple[str, list[dict]]:
        client = self._client()
        emotions_str = ", ".join(analysis.emotions or []) or "unknown"
        keywords_str = ", ".join((analysis.keywords or [])[:10]) or "none"

        prompt = _COPY_PROMPT_TEMPLATE.format(
            filename=content_file.filename,
            genre=analysis.genre or "unknown",
            category=analysis.category or "unknown",
            summary=analysis.summary or "no summary",
            emotions=emotions_str,
            keywords=keywords_str,
            target_audience=analysis.target_audience or "general audience",
            score=analysis.viral_potential_score or 50,
            platforms=", ".join(platforms),
        )

        message = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = message.content[0].text
        return raw, _parse_copy(raw)

    async def list_generated(self, file_id: uuid.UUID) -> list[GeneratedContentResponse]:
        content_file = await self.file_repo.get(file_id)
        if content_file is None:
            raise NotFoundError(f"ContentFile {file_id} not found.")
        items = await self.gen_repo.list_by_file(file_id)
        return [GeneratedContentResponse.model_validate(g) for g in items]
