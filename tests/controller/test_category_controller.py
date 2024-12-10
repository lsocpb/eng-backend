import pytest
from httpx import AsyncClient, ASGITransport

import repos.auction_repo
from db_management.dto import CreateCategory, DeleteCategory
from main import app


@pytest.mark.asyncio
async def test_get_category():
    # get existing category
    from db_management.database_tests import override_get_db
    session = next(override_get_db())
    categories = repos.auction_repo.get_categories(session)
    assert len(categories) > 0
    category_id = categories[0].id

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.get(f"/category/id/{category_id}")
        assert response.status_code == 200

        # test with non-existing category
        response = await ac.get(f"/category/id/1000")
        assert response.status_code == 404

        # test with invalid category id
        response = await ac.get(f"/category/id/abc")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.get(f"/category/all")
        assert response.status_code == 200

        # get count of categories (it should be greater than 0)
        categories = response.json()['categories']
        assert len(categories) > 0


@pytest.mark.asyncio
async def test_create_category():
    category_dto = CreateCategory(name="Test category2", description="Test description")

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.put(f"/category", json=category_dto.dict(), headers={"Content-Type": "application/json"})
        assert response.status_code == 201

        # test with invalid category
        response = await ac.put(f"/category", json={}, headers={"Content-Type": "application/json"})
        assert response.status_code == 422

        # test with existing category
        response = await ac.put(f"/category", json=category_dto.dict(), headers={"Content-Type": "application/json"})
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_delete_category():
    # get existing category
    from db_management.database_tests import override_get_db
    session = next(override_get_db())
    categories = repos.auction_repo.get_categories(session)
    assert len(categories) > 0

    # find special category to delete
    category_id = None
    for category in categories:
        if category.name == "Test category to delete":
            category_id = category
            break
    assert category_id is not None

    category_dto = DeleteCategory(category_id=category_id.id)

    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        response = await ac.request(url=f"/category", method="DELETE", json=category_dto.dict(),
                                    headers={"Content-Type": "application/json"})
        assert response.status_code == 200

        # test with invalid category
        response = await ac.request(url=f"/category", method="DELETE", json={},
                                    headers={"Content-Type": "application/json"})
        assert response.status_code == 422

        # test with already deleted existing category
        response = await ac.request(url=f"/category", method="DELETE", json=category_dto.dict(),
                                    headers={"Content-Type": "application/json"})
        assert response.status_code == 404
