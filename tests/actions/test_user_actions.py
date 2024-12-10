import pytest
from httpx import AsyncClient, ASGITransport

import repos.auction_repo
import repos.user_repo
from db_management.dto import BuyNow, PlaceBid
from main import app


@pytest.mark.asyncio
async def test_buy_now():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        from db_management.database_tests import override_get_db
        session = next(override_get_db())

        # get user token
        user_token = pytest.user_token
        user_id = pytest.user_id
        assert user_token is not None

        # store user balance before buying
        user = repos.user_repo.get_by_id(session, user_id)
        assert user is not None
        user_balance_before = user.get_current_balance

        # get prepared auction
        test_auction_search = repos.auction_repo.search_auctions_by_name(session, "Katana magiczna")
        assert len(test_auction_search) == 1
        test_auction = test_auction_search[0]
        buy_now_dto = BuyNow(auction_id=test_auction.id)

        # purchase auction
        response = await ac.post(f"/auction/buy_now", json=buy_now_dto.dict(),
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200

        # purchase auction already bought (should fail)
        response = await ac.post(f"/auction/buy_now", json=buy_now_dto.dict(),
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 400

        # verify if user has bought the auction
        response = await ac.get(f"/user/purchases", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert len(response.json()) > 0
        assert response.json()['purchases'][0]['id'] == test_auction.id

        # verify if user balance has been deducted
        response = await ac.get(f"/user/wallet", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()['balance_total'] == user_balance_before - test_auction.buy_now_price

        # verify if the auction is inactive
        response = await ac.get(f"/auction/id/{test_auction.id}")
        assert response.status_code == 200
        assert response.json()['buyer']['id'] == user_id
        assert response.json()['is_auction_finished'] is True


# @pytest.mark.asyncio
# async def test_socketio():
#     await run_test()


@pytest.mark.asyncio
async def test_bid():
    async with AsyncClient(transport=ASGITransport(app=app),
                           base_url="http://test", verify=False, follow_redirects=True) as ac:
        from db_management.database_tests import override_get_db
        session = next(override_get_db())

        # get user token
        user_token = pytest.user_token
        user_id = pytest.user_id

        # store user balance before bidding
        user = repos.user_repo.get_by_id(session, user_id)
        assert user is not None
        user_balance_before = user.get_current_balance

        # get prepared auction
        test_auction_search = repos.auction_repo.search_auctions_by_name(session, "Jablko")
        assert len(test_auction_search) == 1
        test_auction = test_auction_search[0]

        # bid on auction
        bid_dto = PlaceBid(auction_id=test_auction.id, bid_value=10)
        response = await ac.post(f"/auction/bid", json=bid_dto.dict(),
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200

        # bid on auction with higher price (should fail, due user is current winner)
        bid_dto.bid_value = 20
        response = await ac.post(f"/auction/bid", json=bid_dto.dict(),
                                 headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 400

        # verify if user balance has been deducted
        response = await ac.get(f"/user/wallet", headers={"Authorization": f"Bearer {user_token}"})
        assert response.status_code == 200
        assert response.json()['balance_reserved'] == 15  # 10 + 5 (bid value + starting price)
        assert response.json()['balance_total'] == user_balance_before

        # verify if the auction has been updated
        response = await ac.get(f"/auction/id/{test_auction.id}")
        assert response.status_code == 200
        assert response.json()['bid']['current_bid_value'] == 15
        assert response.json()['bid']['current_bid_winner']['id'] == user_id
        assert response.json()['is_auction_finished'] is False
