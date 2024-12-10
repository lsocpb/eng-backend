import asyncio
from datetime import datetime, timedelta

import pytest

import repos.auction_repo
import repos.user_repo
import services.email_service
from db_management.dto import PersonalRegisterForm, AccountDetails, PersonalBilling, CompanyBilling, \
    CompanyRegisterForm, CreateCategory, CreateAuction, CreateAuctionProduct
from main import start_socketio, start_socketio_sync
from response_models.auth_responses import create_access_token
from services.auction_service import create_auction
from services.user_service import create_personal_account, create_company_account
from utils.constants import AuctionType, UserAccountType


def pytest_configure():
    pytest.personal_account_token = "empty"
    pytest.company_account_token = "empty"


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    # Disable sending real emails
    services.email_service.send_real_emails = False

    from db_management.database_tests import override_get_db
    session = next(override_get_db())

    category = repos.auction_repo.create_category(
        session, CreateCategory(name="Test category", description="Test description")
    )
    assert category is not None

    # another category for category deletion test
    category2 = repos.auction_repo.create_category(
        session,
        CreateCategory(name="Test category to delete", description="Test description"),
    )
    assert category2 is not None

    personal_data = PersonalRegisterForm(
        account_details=AccountDetails(
            username="andriej11", password="Dawid123!", email="andrzej.nowak@gmail.com"
        ),
        billing_details=PersonalBilling(
            first_name="Andrzej",
            last_name="Nowak",
            address="Młynowa 11",
            postal_code="15-369",
            city="Białystok",
            state="Podlaskie",
            country="Poland",
            phone_number="515555454",
        ),
    )

    company_data = CompanyRegisterForm(
        account_details=AccountDetails(
            username="nowy1121", password="Dawid123!", email="ceo@zetu.com"
        ),
        billing_details=CompanyBilling(
            company_name="ZETU SA",
            tax_id="1190982738",
            address="Warszawska 62",
            postal_code="15-077",
            city="Białystok",
            state="Podlaskie",
            country="Poland",
            phone_number="515555454",
            bank_account="PL06109024028237151822197338",
        ),
    )

    # create sample auction
    auction_data = CreateAuction(
        auction_type=AuctionType.BID,
        end_date=datetime.now() + timedelta(days=1),
        price=5,
        product=CreateAuctionProduct(
            name="Jablko",
            description="Zdrowe jablko w super cenie",
            category_id=category.id,
            images=["http://res.cloudinary.com/sample-image.jpg"],
        ),
    )

    # create auction buy now
    auction_data2 = CreateAuction(
        auction_type=AuctionType.BUY_NOW,
        end_date=datetime.now() + timedelta(days=1),
        price=1,
        product=CreateAuctionProduct(
            name="Katana magiczna",
            description="Prawdziwa katana w super cenie",
            category_id=category.id,
            images=["http://res.cloudinary.com/sample-image.jpg"],
        ),
    )

    personal_account = create_personal_account(session, personal_data)
    assert personal_account is not None
    company_account = create_company_account(session, company_data)
    assert company_account is not None

    # activate business account
    company_account.account_type = UserAccountType.BUSINESS

    # add balance to user
    personal_account.balance_total = 1000

    # save changes
    session.commit()

    # create sample auction
    create_auction(session, auction_data, company_account.id)
    create_auction(session, auction_data2, company_account.id)

    # create and store tokens
    pytest.user_token = create_access_token(personal_account)
    pytest.company_account_token = create_access_token(company_account)
    pytest.user_id = personal_account.id
    pytest.company_account_id = company_account.id

    yield  # this is where the testing happens

    session.commit()


async def start_socketio_test():
    print("Serwer Socket.IO uruchomiony")
    await asyncio.sleep(30)  # Symulacja działania serwera


# @pytest.fixture(scope="session", autouse=True)
# async def async_server():
#     print("Starting async server")
#     task = asyncio.create_task(start_socketio())  # Uruchamia serwer w tle
#     yield  # Pozwala kontynuować testy, gdy serwer działa w tle
#     task.cancel()  # Anuluje zadanie po zakończeniu testów
#     try:
#         await task  # Upewnia się, że zadanie zostało anulowane poprawnie
#     except asyncio.CancelledError:
#         print("Serwer Socket.IO został anulowany")

# @pytest.fixture(scope="session", autouse=True)
# def async_server():
#     print("Starting async server")
#     start_socketio_sync()
