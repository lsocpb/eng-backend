from datetime import datetime

import repos.auction_repo
import repos.user_repo
import services.purcharse_service
from db_management.dto import CreateAuction, CreateAuctionProduct
from utils.constants import AuctionType


def create_sample_auction() -> CreateAuction:
    image = ["http://res.cloudinary.com/dsfdvlauw/image/upload/v1729090419/kjqwpkyxr4gfrmvtyhvu.jpg"]
    product = CreateAuctionProduct(name="Drzewo mądrości", description="Drzewo mądrości", category_id=1, images=image)

    custom_date = datetime(2024, 10, 20, 12, 30, 0)  # Custom date and time
    auction = CreateAuction(auction_type=AuctionType.BID, end_date=custom_date, price=1.0,
                            product=product)
    print(auction.dict())

    return auction


if __name__ == '__main__':
    from db_management.database import create_db

    create_db()

    user = repos.user_repo.get_by_id(5)
    if user is None:
        raise ValueError("User not found")

    auction = repos.auction_repo.get_full_auction_by_id(3)
    if auction is None:
        raise ValueError("Auction already exists")

    print(f"Auction: {auction} User: {user} User bought: {user.products_bought}")
    # repos.user_repo.add_user_bought_product(user, auction)

    # services.purcharse_service.place_bid(auction.id, user.id, 5.12345678)
