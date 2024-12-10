import pytest
from httpx import AsyncClient, ASGITransport

import repos.auction_repo
from db_management.dto import BuyNow
from main import app


@pytest.mark.asyncio
async def test_me():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        # Test personal account
        response = await ac.get(f"/user/me", headers={"Authorization": f"Bearer {pytest.user_token}"})
        assert response.status_code == 200

        # Test company account
        response = await ac.get(f"/user/me", headers={"Authorization": f"Bearer {pytest.company_account_token}"})
        assert response.status_code == 200

        # Test invalid token
        response = await ac.get(f"/user/me", headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code == 401

        # Test no token
        response = await ac.get(f"/user/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_purchases():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        # Test personal account (should fail)
        response = await ac.get(f"/user/sales", headers={"Authorization": f"Bearer {pytest.user_token}"})
        assert response.status_code == 403

        # Test company account
        response = await ac.get(f"/user/sales", headers={"Authorization": f"Bearer {pytest.company_account_token}"})
        assert response.status_code == 200

        # Test invalid token
        response = await ac.get(f"/user/sales", headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code == 401

        # Test no token
        response = await ac.get(f"/user/sales")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_sales():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        # Test personal account
        response = await ac.get(f"/user/purchases", headers={"Authorization": f"Bearer {pytest.user_token}"})
        assert response.status_code == 200

        # Test company account (should fail)
        response = await ac.get(f"/user/purchases", headers={"Authorization": f"Bearer {pytest.company_account_token}"})
        assert response.status_code == 403

        # Test invalid token
        response = await ac.get(f"/user/purchases", headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code == 401

        # Test no token
        response = await ac.get(f"/user/purchases")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_user_wallet_balance():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        # Test personal account
        response = await ac.get(f"/user/wallet", headers={"Authorization": f"Bearer {pytest.user_token}"})
        assert response.status_code == 200
        assert response.json()['balance_total'] > 0

        # Test invalid token
        response = await ac.get(f"/user/wallet", headers={"Authorization": f"Bearer invalid_token"})
        assert response.status_code == 401

        # Test no token
        response = await ac.get(f"/user/wallet")
        assert response.status_code == 401




