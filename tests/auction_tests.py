from datetime import datetime

from sqlalchemy.orm import selectinload

import repos.auction_repo
import repos.user_repo
from db_management.database import session_maker
from db_management.dto import CreateAuction, CreateAuctionProduct
from db_management.models import User
from utils.constants import AuctionType


def create_sample_auction() -> CreateAuction:
    image = ["http://res.cloudinary.com/dsfdvlauw/image/upload/v1729090419/kjqwpkyxr4gfrmvtyhvu.jpg"]
    product = CreateAuctionProduct(name="Drzewo mądrości", description="Drzewo mądrości", category_id=1, images=image)

    custom_date = datetime(2024, 10, 20, 12, 30, 0)  # Custom date and time
    auction = CreateAuction(auction_type=AuctionType.BID, quantity=1, end_date=custom_date, price=1.0,
                            product=product)
    print(auction.dict())

    return auction


def a():
    with session_maker() as session:
        return session.query(User).options(
            selectinload(User.address)  # load the address relationship
        ).all()


if __name__ == '__main__':
    from db_management.database import create_db
    create_db()

    user = repos.user_repo.get_by_id(3)
    if user is None:
        raise ValueError("User not found")

    get_latest_auctions = repos.auction_repo.get_latest_auctions()
    for auction in get_latest_auctions:
        print(auction)

    # auction = create_sample_auction()

    # repos.auction_repo.create_auction(auction, user)
