from __future__ import annotations

import io
import uuid

import pytest
from httpx import AsyncClient


def _small_mp4() -> bytes:
    """
    Minimal valid-ish MP4 bytes sufficient for multipart upload testing.
    Not a real playable video — just enough to test the upload pathway.
    """
    # ftyp box: 4-byte size + "ftyp" + "mp42" + 4-byte minor + "mp42"
    ftyp = b"\x00\x00\x00\x14ftypisom\x00\x00\x00\x00isommp42"
    # mdat box with a tiny payload
    mdat = b"\x00\x00\x00\x10mdat" + b"\x00" * 8
    return ftyp + mdat


@pytest.mark.asyncio
async def test_upload_video(async_client: AsyncClient) -> None:
    payload = _small_mp4()
    response = await async_client.post(
        "/api/v1/uploads",
        files={"file": ("test.mp4", io.BytesIO(payload), "video/mp4")},
        data={"caption": "My first Reel"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["original_filename"] == "test.mp4"
    assert data["media_type"] == "video"
    assert data["status"] == "ready"
    assert data["caption"] == "My first Reel"


@pytest.mark.asyncio
async def test_list_uploads(async_client: AsyncClient) -> None:
    # Upload something first so the list is non-empty.
    await async_client.post(
        "/api/v1/uploads",
        files={"file": ("list_test.mp4", io.BytesIO(_small_mp4()), "video/mp4")},
    )

    response = await async_client.get("/api/v1/uploads")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_delete_upload(async_client: AsyncClient) -> None:
    # Create an upload.
    create_resp = await async_client.post(
        "/api/v1/uploads",
        files={"file": ("delete_me.mp4", io.BytesIO(_small_mp4()), "video/mp4")},
    )
    assert create_resp.status_code == 201
    upload_id = create_resp.json()["id"]

    # Delete it.
    delete_resp = await async_client.delete(f"/api/v1/uploads/{upload_id}")
    assert delete_resp.status_code == 204

    # Confirm it's gone.
    get_resp = await async_client.get(f"/api/v1/uploads/{upload_id}")
    assert get_resp.status_code == 404
