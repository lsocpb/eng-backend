from datetime import datetime

import repos.auction_repo
import repos.user_repo
from db_management.dto import CreateAuction, CreateAuctionProduct
from utils.constants import AuctionType, AuctionStatus


def create_sample_auction() -> CreateAuction:
    image = ["http://res.cloudinary.com/dsfdvlauw/image/upload/v1729090419/kjqwpkyxr4gfrmvtyhvu.jpg"]
    product = CreateAuctionProduct(name="Drzewo mądrości", description="Drzewo mądrości", category_id=1, images=image)

    custom_date = datetime(2024, 10, 20, 12, 30, 0)  # Custom date and time
    auction = CreateAuction(auction_type=AuctionType.BID, end_date=custom_date, price=1.0,
                            product=product)
    print(auction.dict())

    return auction


if __name__ == '__main__':
    from db_management.database import create_db, session_maker

    create_db()
    # get session
    with session_maker() as session:
        user = repos.user_repo.get_by_id(session, 3)
        if user is None:
            raise ValueError("User not found")

        auction = repos.auction_repo.get_auction_by_id(session, 4)
        if auction is None:
            raise ValueError("Auction already exists")

        # repos.auction_repo.add_user_auction_buyer(auction=auction, user=user)
        # repos.auction_repo.set_auction_status(auction, AuctionStatus.INACTIVE)
        print(f"Auction: {auction.product.name} User: {user.username} User selling: {user.products_sold}")

        # user = repos.user_repo.get_by_id(session, 4)
        # auction = repos.auction_repo.get_auction_by_id(session, 3)
        # print(f"Auction: {auction.auction_status} User: {user} User bought: {user.products_bought}")

        # session.commit()
        # input("Click to rollback")
        # session.rollback()

    # services.purcharse_service.place_bid(auction.id, user.id, 5.12345678)
