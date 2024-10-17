from sqlalchemy.orm import selectinload

from db_management.database import session_maker
from db_management.dto import CreateAuction, CreateCategory
from db_management.models import Auction, Product, Category, User, Bid, BidHistory, BidParticipant
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


def get_category_by_id(category_id: int) -> Category | None:
    with session_maker() as session:
        return session.query(Category).where(Category.id == category_id).first()


def get_categories() -> list[Category]:
    with session_maker() as session:
        return session.query(Category).all()


def delete_category(category_id: int) -> None:
    with session_maker() as session:
        category = session.query(Category).where(Category.id == category_id).first()
        session.delete(category)
        session.commit()


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


def delete_auction(auction_id: int) -> None:
    with session_maker() as session:
        auction = session.query(Auction).where(Auction.id == auction_id).first()
        session.delete(auction)
        session.commit()


def get_auction_by_id(auction_id: int) -> Auction | None:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product),
            selectinload(Auction.bid),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).where(Auction.id == auction_id).first()


def get_full_auction_by_id(auction_id: int) -> Auction | None:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product).selectinload(Product.category),
            selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
            selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).where(Auction.id == auction_id).first()


def get_auction_by_bid_id(bid_id: int) -> Auction | None:
    with session_maker() as session:
        return session.query(Auction).where(Auction.bid_id == bid_id).first()


def get_latest_auctions(amount: int = 5) -> list[Auction]:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product).selectinload(Product.category),
            selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
            selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).order_by(Auction.created_at.desc()).limit(amount).all()


def get_auction_list_by_category(category_id: int, limit: int = 5) -> list[Auction]:
    with session_maker() as session:
        return session.query(Auction).options(
            selectinload(Auction.product).selectinload(Product.category),  # load the bid_history relationship
            selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
            selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
            selectinload(Auction.seller),
            selectinload(Auction.buyer)
        ).join(Product).filter(Product.category_id == category_id).limit(limit).all()


def add_user_auction_buyer(auction: Auction, user: User) -> None:
    with session_maker() as session:
        auction.buyer = user
        session.add(auction)
        session.commit()


def set_auction_status(auction: Auction, status: str) -> None:
    with session_maker() as session:
        auction.status = status
        session.add(auction)
        session.commit()


def is_user_bid_participant(auction: Auction, user: User) -> bool:
    with session_maker() as session:
        return session.query(BidParticipant).join(BidHistory, BidParticipant.bid_id == BidHistory.bid_id) \
            .filter(BidParticipant.bid_id == auction.bid.id, BidHistory.user_id == user.id).first() is not None


# return current active auction id if user is participating in an active auction, else return 0
def get_user_active_bid_participant(user_id: int) -> int:
    with session_maker() as session:
        # first get all the auctions the user is participating in
        user_bid_participant = session.query(BidParticipant).where(BidParticipant.user_id == user_id).all()
        if not user_bid_participant:
            return 0

        # then count how many of them are still active
        for bid in user_bid_participant:
            auction = get_auction_by_bid_id(bid.bid_id)
            if auction:
                if not auction.is_auction_finished:
                    return auction.id

        return 0


def create_bid_history_entry(auction: Auction, user: User, amount: float) -> None:
    with session_maker() as session:
        bid_history_entry = BidHistory(
            bid=auction.bid,
            user=user,
            amount=amount
        )
        session.add(bid_history_entry)
        session.commit()


def add_bid_participant(auction: Auction, user: User) -> None:
    if not is_user_bid_participant(auction, user):
        with session_maker() as session:
            bid_participant = BidParticipant(
                bid=auction.bid,
                user=user
            )
            session.add(bid_participant)
            session.commit()


def update_bid_winner(auction: Auction, user: User, amount: float) -> None:
    with session_maker() as session:
        auction.bid.current_bid_winner = user
        auction.bid.current_bid_value = amount
        session.add(auction)
        session.commit()
