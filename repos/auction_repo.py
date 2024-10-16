from sqlalchemy.orm import selectinload

from db_management.database import session_maker
from db_management.dto import CreateAuction, CreateCategory
from db_management.models import Auction, Product, Category, User, Bid
from utils.constants import AuctionType


def create_category(category: CreateCategory) -> Category:
    with session_maker() as session:
        db_category = Category(
            name=category.name,
            description=category.description,
            icon=category.icon
        )
        session.add(db_category)
        session.commit()
        session.refresh(db_category)
        return db_category


def create_auction(auction: CreateAuction, user: User) -> Auction:
    with session_maker() as session:
        product = Product(
            name=auction.product.name,
            description=auction.product.description,
            category_id=auction.product.category_id,
            image_url_1=auction.product.images[0],
            image_url_2=auction.product.images[1] if len(auction.product.images) > 1 else None,
            image_url_3=auction.product.images[2] if len(auction.product.images) > 2 else None
        )
        db_auction = Auction(
            auction_type=auction.auction_type,
            quantity=auction.quantity,
            end_date=auction.end_date,
            product=product
        )

        # Set the seller
        db_auction.seller = user

        # Set the price based on the auction type
        if auction.auction_type == AuctionType.BID:
            bid = Bid(
                current_bid_value=auction.price,
            )
            db_auction.bid = bid
        else:
            db_auction.buy_now_price = auction.price

        session.add(db_auction)
        session.commit()
        session.refresh(db_auction)
        return db_auction


def get_auction_by_id(auction_id: int) -> Auction | None:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product),  # load the bid_history relationship
            selectinload(Auction.bid),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).where(Auction.id == auction_id).first()


def get_latest_auctions() -> list[Auction]:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product),  # load the bid_history relationship
            selectinload(Auction.bid),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).order_by(Auction.created_at.desc()).limit(10).all()
