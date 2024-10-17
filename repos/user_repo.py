from sqlalchemy import Delete
from sqlalchemy.orm import selectinload, Session, object_session

from db_management.models import User


def get_by_id(session: Session, user_id: int) -> User:
    return session.query(User).where(User.id == user_id).options(
        selectinload(User.address),
        selectinload(User.products_bought),
        selectinload(User.products_sold)
    ).first()


def delete(session: Session, user_id: int) -> None:
    session.execute(Delete(User).where(User.id == user_id))


def update_user_profile_image(user: User, profile_image_url: str) -> None:
    if not object_session(user):
        raise ValueError("Session not found")

    user.profile_image_url = profile_image_url


def set_frozen_balance(user: User, amount: float) -> None:
    if not object_session(user):
        raise ValueError("Session not found")

    user.balance_reserved = amount


def deduct_total_balance(user: User, amount: float) -> None:
    if not object_session(user):
        raise ValueError("Session not found")
    if user.balance_total < amount:
        raise ValueError("Insufficient balance")

    user.balance_total -= amount
