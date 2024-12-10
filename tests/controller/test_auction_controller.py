import pytest
from httpx import AsyncClient, ASGITransport

import repos.auction_repo
from main import app


@pytest.mark.asyncio
async def test_get_auction_by_id():
    # get existing auction
    from db_management.database_tests import override_get_db
    session = next(override_get_db())
    auctions = repos.auction_repo.get_all_auctions(session)
    assert len(auctions) > 0
    auction_id = auctions[0].id

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        # content-type: application/x-www-form-urlencoded
        response = await ac.get(f"/auction/id/{auction_id}")
        assert response.status_code == 200

        # test with non-existing auction
        response = await ac.get(f"/auction/id/1000", headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 404

        # test with invalid auction id
        response = await ac.get(f"/auction/id/abc", headers={"Content-Type": "application/x-www-form-urlencoded"})
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_latest():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.get("/auction/last")
        assert response.status_code == 200

        # get count of products (it should be greater than 0)
        products = response.json()['products']
        assert len(products) > 0


@pytest.mark.asyncio
async def test_search():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        data = {"keyword": "Katana"}
        response = await ac.post("/auction/search", headers={"Content-Type": "application/json"}, json=data)
        assert response.status_code == 200

        # get count of products (it should be greater than 0)
        auctions = response.json()['auctions']
        assert len(auctions) > 0

        # test with non-existing auction
        data = {"keyword": "Non-existing auction"}
        response = await ac.post("/auction/search", headers={"Content-Type": "application/json"}, json=data)
        assert response.status_code == 404

        # test with invalid keyword
        data = {"test": ""}
        response = await ac.post("/auction/search", headers={"Content-Type": "application/json"}, json=data)
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_auctions_by_category():
    # get existing category
    from db_management.database_tests import override_get_db
    session = next(override_get_db())
    categories = repos.auction_repo.get_categories(session)
    assert len(categories) > 0
    category_id = categories[0].id

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.get(f"/auction/category/{category_id}")
        assert response.status_code == 200

        # get count of products (it should be greater than 0)
        auctions = response.json()['auctions']
        assert len(auctions) > 0

        # test with non-existing category
        response = await ac.get(f"/auction/category/1000")
        assert response.status_code == 404

        # test with invalid category id
        response = await ac.get(f"/auction/category/abc")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_auctions_stats():
    # get existing auction
    from db_management.database_tests import override_get_db
    session = next(override_get_db())
    auctions = repos.auction_repo.get_all_auctions(session)
    assert len(auctions) > 0
    auction_id = auctions[0].id

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.get(f"/auction/stats/{auction_id}")
        assert response.status_code == 200

        # test with non-existing auction
        response = await ac.get(f"/auction/stats/1000")
        assert response.status_code == 404
