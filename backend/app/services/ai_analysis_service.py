from __future__ import annotations

import asyncio
import base64
import json
import logging
import subprocess
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from openai import OpenAI

from app.core.config import settings
from app.core.exceptions import NotFoundError, ValidationError
from app.repositories.ai_analysis_repository import AiAnalysisRepository
from app.repositories.content_file_repository import ContentFileRepository
from app.schemas.ai_analysis import AiAnalysisResponse

logger = logging.getLogger(__name__)

MODEL = "gpt-4o"
MAX_FRAMES = 6
FRAME_QUALITY = 2  # ffmpeg -q:v: 1=best, 31=worst


_ANALYSIS_PROMPT = """\
You are a social media content analyst. Analyze the provided content and return a JSON object with EXACTLY these keys:

{
  "scenes": ["list of scene descriptions"],
  "objects": ["list of notable objects/subjects visible"],
  "activities": ["list of activities or actions happening"],
  "emotions": ["list of moods/emotions conveyed"],
  "genre": "single genre label (e.g. hip-hop, comedy, lifestyle, fitness)",
  "category": "single category (e.g. music, entertainment, education, sports)",
  "summary": "2-3 sentence description of what this content is about",
  "keywords": ["10-15 relevant search/hashtag keywords, no # prefix"],
  "target_audience": "description of ideal viewer demographic",
  "viral_potential_score": <integer 1-100>
}

Be specific and creative. For music content, identify the vibe, energy, and style.
Return ONLY the JSON object, no markdown fences, no explanation."""


_AUDIO_PROMPT_TEMPLATE = """\
You are a social media content analyst. Analyze the following audio file metadata and return a JSON analysis.

File: {filename}
File type: {file_type}
Size: {size_mb:.1f} MB
Duration: {duration}
MIME type: {mime_type}

Based on the filename and context (this appears to be a music/audio file), provide a creative analysis as if you heard the track. Use the filename to infer genre, style, and content.

Return a JSON object with EXACTLY these keys:
{{
  "scenes": ["visual scenes this audio would pair with"],
  "objects": ["instruments or sound elements likely present"],
  "activities": ["activities this audio would suit"],
  "emotions": ["moods/emotions this audio likely conveys"],
  "genre": "single genre label",
  "category": "music",
  "summary": "2-3 sentence description based on filename/context",
  "keywords": ["10-15 relevant keywords for social media"],
  "target_audience": "description of ideal audience",
  "viral_potential_score": <integer 1-100>
}}

Return ONLY the JSON object."""


def _extract_frames(video_path: str, max_frames: int = MAX_FRAMES) -> list[str]:
    """Extract up to max_frames evenly spaced frames. Returns list of base64 JPEG strings."""
    with tempfile.TemporaryDirectory() as tmpdir:
        out_pattern = str(Path(tmpdir) / "frame_%03d.jpg")
        # Try select filter first, fall back to fps
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"select=not(mod(n\\,max(1\\,trunc(n_frames/{max_frames}))))",
            "-vsync", "vfr",
            "-frames:v", str(max_frames),
            "-q:v", str(FRAME_QUALITY),
            out_pattern,
            "-y", "-loglevel", "error",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode != 0:
            dur = _get_duration(video_path)
            interval = max(1, dur // max_frames)
            cmd2 = [
                "ffmpeg", "-i", video_path,
                "-vf", f"fps=1/{interval}",
                "-frames:v", str(max_frames),
                "-q:v", str(FRAME_QUALITY),
                out_pattern,
                "-y", "-loglevel", "error",
            ]
            subprocess.run(cmd2, capture_output=True, timeout=60)

        frames = []
        for img_path in sorted(Path(tmpdir).glob("frame_*.jpg")):
            with open(img_path, "rb") as f:
                frames.append(base64.b64encode(f.read()).decode())
        return frames


def _get_duration(video_path: str) -> int:
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                video_path,
            ],
            capture_output=True, text=True, timeout=15,
        )
        return int(float(result.stdout.strip()))
    except Exception:
        return 60


def _parse_analysis(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])
    return json.loads(text)


class AiAnalysisService:
    def __init__(
        self,
        file_repo: ContentFileRepository,
        analysis_repo: AiAnalysisRepository,
    ) -> None:
        self.file_repo = file_repo
        self.analysis_repo = analysis_repo

    def _client(self) -> OpenAI:
        if not settings.OPENAI_API_KEY:
            raise ValidationError(
                "OPENAI_API_KEY is not configured. Add it to .env to enable AI analysis."
            )
        return OpenAI(api_key=settings.OPENAI_API_KEY)

    async def analyze_file(self, file_id: uuid.UUID) -> AiAnalysisResponse:
        content_file = await self.file_repo.get(file_id)
        if content_file is None:
            raise NotFoundError(f"ContentFile {file_id} not found.")

        await self.file_repo.update(file_id, {"status": "analyzing"})

        try:
            raw_response, parsed = await asyncio.get_event_loop().run_in_executor(
                None, self._run_openai, content_file
            )
        except Exception as exc:
            await self.file_repo.update(
                file_id, {"status": "failed", "error_message": str(exc)}
            )
            raise

        now = datetime.now(tz=timezone.utc)

        analysis_data = {
            "content_file_id": file_id,
            "scenes": parsed.get("scenes") or [],
            "objects": parsed.get("objects") or [],
            "activities": parsed.get("activities") or [],
            "emotions": parsed.get("emotions") or [],
            "genre": parsed.get("genre"),
            "category": parsed.get("category"),
            "summary": parsed.get("summary"),
            "keywords": parsed.get("keywords") or [],
            "target_audience": parsed.get("target_audience"),
            "viral_potential_score": parsed.get("viral_potential_score"),
            "raw_response": {"text": raw_response},
            "analyzed_at": now,
            "model_used": MODEL,
        }

        existing = await self.analysis_repo.get_by_file(file_id)
        if existing is not None:
            analysis = await self.analysis_repo.update(existing.id, analysis_data)
        else:
            analysis = await self.analysis_repo.create(analysis_data)

        await self.file_repo.update(file_id, {"status": "analyzed"})
        return AiAnalysisResponse.model_validate(analysis)

    def _run_openai(self, content_file) -> tuple[str, dict]:
        client = self._client()
        if content_file.file_type == "video":
            return self._analyze_video(client, content_file)
        return self._analyze_audio(client, content_file)

    def _analyze_video(self, client: OpenAI, content_file) -> tuple[str, dict]:
        logger.info("Extracting frames from %s", content_file.file_path)
        frames = _extract_frames(content_file.file_path)

        if not frames:
            raise ValidationError(f"Could not extract frames from {content_file.filename}")

        content: list[dict] = []
        for frame_b64 in frames:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{frame_b64}",
                    "detail": "low",
                },
            })
        content.append({"type": "text", "text": _ANALYSIS_PROMPT})

        logger.info("Sending %d frames to GPT-4o for %s", len(frames), content_file.filename)
        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": content}],
        )
        raw = response.choices[0].message.content or ""
        return raw, _parse_analysis(raw)

    def _analyze_audio(self, client: OpenAI, content_file) -> tuple[str, dict]:
        size_mb = (content_file.file_size_bytes or 0) / (1024 * 1024)
        duration = "unknown"
        if content_file.duration_seconds:
            m, s = divmod(int(content_file.duration_seconds), 60)
            duration = f"{m}:{s:02d}"

        prompt = _AUDIO_PROMPT_TEMPLATE.format(
            filename=content_file.filename,
            file_type=content_file.file_type,
            size_mb=size_mb,
            duration=duration,
            mime_type=content_file.mime_type or "audio",
        )

        response = client.chat.completions.create(
            model=MODEL,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.choices[0].message.content or ""
        return raw, _parse_analysis(raw)

    async def get_analysis(self, file_id: uuid.UUID) -> AiAnalysisResponse:
        analysis = await self.analysis_repo.get_by_file(file_id)
        if analysis is None:
            raise NotFoundError(f"No analysis found for file {file_id}. Run analyze first.")
        return AiAnalysisResponse.model_validate(analysis)
