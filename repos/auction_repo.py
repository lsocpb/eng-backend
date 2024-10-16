from sqlalchemy import Update, Delete
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import current_timestamp

from db_management.database import session_maker
from db_management.models import Bid, BidHistory, BidParticipant


def get_by_id(user_id: int) -> Bid | None:
    with session_maker() as session:
        return session.query(Bid).options(
            selectinload(Bid.bid_history),  # load the bid_history relationship
            selectinload(Bid.bid_participants)  # load the bid_participants relationship
        ).where(Bid.id == user_id).first()

