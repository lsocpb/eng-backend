from sqlalchemy.orm import selectinload, Session, object_session

from db_management.dto import CreateCategory
from db_management.models import Auction, Product, Category, User, Bid, BidHistory, BidParticipant
from utils.constants import AuctionStatus
from utils.constants import fastapi_logger as logger


def create_category(session: Session, category: CreateCategory) -> Category | None:
    if get_category_by_name(session, category.name) is not None:
        return None

    db_category = Category(
        name=category.name,
        description=category.description,
        icon=category.icon
    )
    session.add(db_category)
    session.commit()
    session.refresh(db_category)
    return db_category


def get_category_by_id(session: Session, category_id: int) -> Category | None:
    return session.query(Category).where(Category.id == category_id).first()


def get_category_by_name(session: Session, category_name: str) -> Category | None:
    return session.query(Category).where(Category.name == category_name).first()


def get_categories(session: Session) -> list[Category]:
    return session.query(Category).all()


def delete_category(session: Session, category_id: int) -> bool:
    category = session.query(Category).where(Category.id == category_id).first()
    if category is None:
        return False
    session.delete(category)
    session.commit()
    return True


def create_auction(session: Session, auction: Auction):
    session.add(auction)


def delete_auction(session: Session, auction_id: int) -> None:
    auction = session.query(Auction).where(Auction.id == auction_id).first()
    session.delete(auction)


def get_auction_by_id(session: Session, auction_id: int) -> Auction | None:
    return session.query(Auction).options(
        selectinload(Auction.product),
        selectinload(Auction.bid),
        selectinload(Auction.seller),
        selectinload(Auction.buyer)
    ).where(Auction.id == auction_id).first()


def get_full_auction_by_id(session: Session, auction_id: int) -> Auction | None:
    return session.query(Auction).options(
        selectinload(Auction.product).selectinload(Product.category),
        selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
        selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
        selectinload(Auction.seller),
        selectinload(Auction.buyer)
    ).where(Auction.id == auction_id).first()


def get_all_auctions(session: Session) -> list[Auction] | None:
    return session.query(Auction).all()


def get_auction_by_bid_id(session: Session, bid_id: int) -> Auction | None:
    return session.query(Auction).where(Auction.bid_id == bid_id).first()


def get_latest_auctions(session: Session, amount: int = 5):
    return session.query(Auction).options(
        selectinload(Auction.product).selectinload(Product.category),
        selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
        selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
        selectinload(Auction.seller),
        selectinload(Auction.buyer)
    ).order_by(Auction.created_at.desc()).limit(amount).all()


def get_auction_list_by_category(session: Session, category_id: int):
    return session.query(Auction).options(
        selectinload(Auction.product).selectinload(Product.category),
        selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
        selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
        selectinload(Auction.seller),
        selectinload(Auction.buyer)
    ).join(Product).filter(Product.category_id == category_id).all()


def search_auctions_by_name(session: Session, search: str):
    return session.query(Auction).options(
        selectinload(Auction.product).selectinload(Product.category),
        selectinload(Auction.bid).selectinload(Bid.bidders).selectinload(BidParticipant.user),
        selectinload(Auction.bid).selectinload(Bid.current_bid_winner),
        selectinload(Auction.seller),
        selectinload(Auction.buyer)
    ).join(Product).filter(Product.name.ilike(f"%{search}%")).all()


def add_user_auction_buyer(auction: Auction, user: User) -> None:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")
    auction.buyer = user


def set_auction_status(auction: Auction, status: AuctionStatus) -> None:
    if not object_session(auction):
        raise ValueError("Auction must be attached to a session")
    auction.auction_status = status


def is_user_bid_participant(session: Session, auction: Auction, user: User) -> bool:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")

    return session.query(BidParticipant).join(BidHistory, BidParticipant.bid_id == BidHistory.bid_id) \
        .filter(BidParticipant.bid_id == auction.bid.id, BidHistory.user_id == user.id).first() is not None


# make sure the user is not participating in a different active auction
def is_user_participating_in_different_active_bid(session: Session, auction: Auction, user: User) -> bool:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")

    # first get all the auctions the user have ever participated in (even if they are finished)
    user_bid_participant_list = session.query(BidParticipant).where(BidParticipant.user_id == user.id).all()
    if not user_bid_participant_list:
        return False

    # iterate over all the auctions the user have ever participated in
    for bid_participant in user_bid_participant_list:
        loop_auction = get_auction_by_bid_id(session, bid_participant.bid_id)
        if not loop_auction:
            logger.warning(f"User {user.id} is participating in a non-existent auction {bid_participant.bid_id}")
            continue

        # skip the current auction
        if loop_auction.id == auction.id:
            continue

        # check if the auction does not have finished yet
        if not loop_auction.is_auction_finished:
            return True

    return False


def create_bid_history_entry(session: Session, auction: Auction, user: User, amount: float) -> None:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")

    bid_history_entry = BidHistory(
        bid=auction.bid,
        user=user,
        amount=amount
    )
    session.add(bid_history_entry)


def add_bid_participant(session: Session, auction: Auction, user: User) -> None:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")

    if not is_user_bid_participant(session, auction, user):
        bid_participant = BidParticipant(
            bid=auction.bid,
            user=user
        )
        session.add(bid_participant)


def update_bid_winner(auction: Auction, user: User, amount: float) -> None:
    if not object_session(auction) or not object_session(user):
        raise ValueError("Both auction and user must be attached to a session")

    auction.bid.current_bid_winner = user
    auction.bid.current_bid_value = amount
