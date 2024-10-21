import repos.auction_repo
import repos.user_repo
from db_management.dto import CreateAuction, CreateAuctionProduct
from db_management.models import *
from repos.stats_repo import *
from utils.constants import AuctionType


def create_sample_auction() -> CreateAuction:
    image = ["http://res.cloudinary.com/dsfdvlauw/image/upload/v1729090419/kjqwpkyxr4gfrmvtyhvu.jpg"]
    product = CreateAuctionProduct(name="Drzewo mądrości", description="Drzewo mądrości", category_id=1, images=image)

    custom_date = datetime(2024, 10, 20, 12, 30, 0)  # Custom date and time
    auction = CreateAuction(auction_type=AuctionType.BID, end_date=custom_date, price=1.0,
                            product=product)
    print(auction.dict())

    return auction


def stats_test(session: Session):
    auction = repos.auction_repo.get_auction_by_id(session, 4)
    if auction is None:
        raise ValueError("Auction already exists")

    print(f"Auction: {auction.product.name} User: {user.username} User selling: {user.products_sold}")

    print(f"Registered users: {get_registered_useres_count(session)}")
    print(f"Auction count: {get_auction_count(session)}")
    print(f"Total bids: {get_total_bids_count(session)}")
    print(f"Total value of ended auctions: {get_total_value_of_ended_auctions(session)}")


if __name__ == '__main__':
    from db_management.database import create_db, session_maker

    create_db()
    # get session
    with session_maker() as session:
        # user = repos.user_repo.get_by_id(session, 3)
        # if user is None:
        #     raise ValueError("User not found")
        #
        companyBilling1 = CompanyBilling(company_details="company_details1")
        companyBilling2 = CompanyBilling(company_details="company_details2")
        userBilling1 = UserBilling(details="user_details1")
        userBilling2 = UserBilling(details="user_details2")

        u1 = repos.user_repo.get_by_id(session, 3)
        u2 = repos.user_repo.get_by_id(session, 4)
        u3 = repos.user_repo.get_by_id(session, 5)
        u4 = repos.user_repo.get_by_id(session, 6)

        print(u1.billing_details)
        print(u2.billing_details)
        print(u3.billing_details)
        print(u4.billing_details)

        # session.commit()

    # services.auction_service.place_bid(auction.id, user.id, 5.12345678)
