from sqlalchemy import func
from sqlalchemy.orm import Session

from db_management.models import User, Auction, BidHistory, Bid, BidParticipant
from utils.constants import AuctionType, AuctionStatus


def get_registered_useres_count(session: Session) -> int:
    return session.query(User).count()


def get_auction_count(session: Session) -> int:
    return session.query(Auction).count()


def get_total_bids_count(session: Session) -> int:
    return session.query(BidHistory).count()


def get_total_value_of_ended_auctions(db: Session):
    bid_auctions = db.query(func.sum(Bid.current_bid_value)) \
        .join(Auction, Auction.bid_id == Bid.id) \
        .filter(Auction.auction_type == AuctionType.BID) \
        .filter(Auction.auction_status == AuctionStatus.INACTIVE) \
        .scalar()

    buy_now_auctions = db.query(func.sum(Auction.buy_now_price)) \
        .filter(Auction.auction_type == AuctionType.BUY_NOW) \
        .filter(Auction.auction_status == AuctionStatus.INACTIVE) \
        .scalar()

    bid_auctions = bid_auctions or 0
    buy_now_auctions = buy_now_auctions or 0

    return round(bid_auctions + buy_now_auctions, 2)


def get_auction_bid_participants_count(session: Session, bid_id: int) -> int:
    return session.query(BidParticipant).filter(BidParticipant.bid_id == bid_id).count()


def get_auction_total_bids(session: Session, bid_id: int) -> int:
    return session.query(BidHistory).filter(BidHistory.bid_id == bid_id).count()


def get_auction_highest_bid(session: Session, bid_id: int) -> float:
    return session.query(func.max(BidHistory.amount)).filter(BidHistory.bid_id == bid_id).scalar() or 0


def get_auction_lowest_bid(session: Session, bid_id: int) -> float:
    return session.query(func.min(BidHistory.amount)).filter(BidHistory.bid_id == bid_id).scalar() or 0
