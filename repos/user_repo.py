from sqlalchemy import Update, Delete
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import current_timestamp

from db_management.database import session_maker
from db_management.models import User, Auction


def get_by_id(user_id: int) -> User | None:
    with session_maker() as session:
        return session.query(User).where(User.id == user_id).options(
            selectinload(User.address),  # load the address relationship
            selectinload(User.products_bought),  # load the address relationship
            selectinload(User.products_sold)  # load the address relationship
        ).first()


def delete(user_id: int) -> None:
    with session_maker.begin() as session:
        session.execute(Delete(User).where(User.id == user_id))


def update_user_profile_image(id: int, profile_image_url: str) -> None:
    with session_maker.begin() as session:
        session.execute(Update(User).where(User.id == id).values({
            User.profile_image_url: profile_image_url,
            User.updated_at: current_timestamp()
        }))


def set_frozen_balance(user: User, amount: float) -> None:
    with session_maker.begin() as session:
        session.execute(Update(User).where(User.id == user.id).values({
            User.balance_reserved: amount
        }))


def add_user_bought_product(user: User, auction: Auction) -> None:
    with session_maker.begin() as session:
        user.products_bought.append(auction)
        session.add(user)
        session.commit()


def deduct_total_balance(user: User, amount: float) -> None:
    with session_maker.begin() as session:
        session.execute(Update(User).where(User.id == user.id).values({
            User.balance_total: User.balance_total - amount
        }))
