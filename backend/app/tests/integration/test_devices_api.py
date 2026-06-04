from __future__ import annotations

import uuid

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_device(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/devices",
        json={"name": "Integration Test Device", "description": "Created by integration test"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Integration Test Device"
    assert "id" in data
    assert "social_accounts" in data


@pytest.mark.asyncio
async def test_list_devices(async_client: AsyncClient) -> None:
    # Create at least one device first.
    await async_client.post("/api/v1/devices", json={"name": "List Test Device"})

    response = await async_client.get("/api/v1/devices")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


@pytest.mark.asyncio
async def test_get_device(async_client: AsyncClient) -> None:
    # Create a device, then fetch it by ID.
    create_resp = await async_client.post(
        "/api/v1/devices", json={"name": "Fetch Me Device"}
    )
    assert create_resp.status_code == 201
    device_id = create_resp.json()["id"]

    response = await async_client.get(f"/api/v1/devices/{device_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == device_id
    assert data["name"] == "Fetch Me Device"


@pytest.mark.asyncio
async def test_get_device_not_found(async_client: AsyncClient) -> None:
    random_id = str(uuid.uuid4())
    response = await async_client.get(f"/api/v1/devices/{random_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_device(async_client: AsyncClient) -> None:
    create_resp = await async_client.post(
        "/api/v1/devices", json={"name": "Before Update"}
    )
    assert create_resp.status_code == 201
    device_id = create_resp.json()["id"]

    patch_resp = await async_client.patch(
        f"/api/v1/devices/{device_id}",
        json={"name": "After Update", "description": "Now has a description"},
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["name"] == "After Update"
    assert data["description"] == "Now has a description"


@pytest.mark.asyncio
async def test_delete_device(async_client: AsyncClient) -> None:
    create_resp = await async_client.post(
        "/api/v1/devices", json={"name": "Delete Me Device"}
    )
    assert create_resp.status_code == 201
    device_id = create_resp.json()["id"]

    delete_resp = await async_client.delete(f"/api/v1/devices/{device_id}")
    assert delete_resp.status_code == 204

    # Confirm it's gone.
    get_resp = await async_client.get(f"/api/v1/devices/{device_id}")
    assert get_resp.status_code == 404
