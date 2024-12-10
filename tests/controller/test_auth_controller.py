import pytest
from httpx import AsyncClient, ASGITransport

from main import app


@pytest.mark.asyncio
async def test_personal_account_valid():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        request_data = {
            "username": "andriej11",
            "password": "Dawid123!",
        }
        response = await ac.post("/auth/token", data=request_data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

        assert response.status_code == 200

        request_data = {
            "username": "nowy1121",
            "password": "Dawid123!",
        }
        response = await ac.post("/auth/token", data=request_data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

        assert response.status_code == 200


@pytest.mark.asyncio
async def test_personal_account_invalid():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        request_data = {
            "username": "andriej11",
            "password": "BAD_PASSWORD",
        }
        # content-type: application/x-www-form-urlencoded
        response = await ac.post("/auth/token", data=request_data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_invalid():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        request_data = {
            "password": "BAD_PASSWORD",
        }
        # content-type: application/x-www-form-urlencoded
        response = await ac.post("/auth/token", data=request_data,
                                 headers={"Content-Type": "application/x-www-form-urlencoded"})

    assert response.status_code == 422

@pytest.mark.asyncio
async def test_password_reset():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        request_data