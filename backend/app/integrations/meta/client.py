from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.exceptions import PlatformAuthError, PlatformPublishError

logger = logging.getLogger(__name__)

_BASE = "https://graph.facebook.com"


class MetaGraphClient:
    """
    Low-level async HTTP client for the Meta Graph API.
    Each instance is scoped to one access token.
    """

    def __init__(self, access_token: str, version: str = "v21.0") -> None:
        self.access_token = access_token
        self.base_url = f"{_BASE}/{version}"

    def _default_params(self) -> dict[str, str]:
        return {"access_token": self.access_token}

    def _raise_for_status(self, response: httpx.Response) -> None:
        """Map HTTP error codes to domain exceptions."""
        if response.status_code in (401, 403):
            body = _safe_json(response)
            error = body.get("error", {})
            raise PlatformAuthError(
                f"Meta auth error {response.status_code}: "
                f"{error.get('message', response.text)}"
            )
        if response.status_code >= 400:
            body = _safe_json(response)
            error = body.get("error", {})
            raise PlatformPublishError(
                f"Meta API error {response.status_code}: "
                f"{error.get('message', response.text)}"
            )

    async def get(self, path: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a GET request against the Graph API."""
        merged = {**self._default_params(), **(params or {})}
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.get(f"{self.base_url}{path}", params=merged)
        logger.debug("GET %s → %s", path, response.status_code)
        self._raise_for_status(response)
        return response.json()

    async def post(self, path: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Perform a POST request with form-encoded data."""
        merged = {**self._default_params(), **(data or {})}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(f"{self.base_url}{path}", data=merged)
        logger.debug("POST %s → %s", path, response.status_code)
        self._raise_for_status(response)
        return response.json()

    async def post_multipart(
        self,
        path: str,
        files: dict[str, Any],
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Perform a multipart POST (for file uploads)."""
        # access_token must be a URL query param for multipart uploads, not in
        # the form body — Facebook's proxy returns 500 when it's in the body.
        params = self._default_params()
        async with httpx.AsyncClient(timeout=300) as client:
            response = await client.post(
                f"{self.base_url}{path}",
                params=params,
                files=files,
                data=data or {},
            )
        logger.debug("POST multipart %s → %s", path, response.status_code)
        self._raise_for_status(response)
        return response.json()


def _safe_json(response: httpx.Response) -> dict[str, Any]:
    try:
        return response.json()  # type: ignore[no-any-return]
    except Exception:
        return {}
