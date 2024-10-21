from sqlalchemy import Delete
from sqlalchemy.orm import selectinload, Session, object_session

from db_management.models import User, WalletTransaction


def get_by_id(session: Session, user_id: int) -> User:
    return session.query(User).where(User.id == user_id).options(
        selectinload(User.address),
        selectinload(User.products_bought),
        selectinload(User.products_sold),
        selectinload(User.billing_details)
    ).first()


def delete(session: Session, user_id: int) -> None:
    session.execute(Delete(User).where(User.id == user_id))


def update_user_profile_image(session: Session, user: User, profile_image_url: str) -> None:
    if not object_session(user):
        raise ValueError("Session not found")

    user.profile_image_url = profile_image_url
    session.commit()


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


def create_wallet_transaction(session: Session, user: User, amount: float, uuid: str, checkout_session_id: str) -> None:
    if not object_session(user):
        raise ValueError("Session not found")

    transaction = WalletTransaction(user_id=user.id, amount=amount, uuid=uuid,
                                    stripe_checkout_session_id=checkout_session_id)

    session.add(transaction)
    session.commit()


def get_wallet_transaction_by_uuid(session: Session, uuid: str) -> WalletTransaction:
    return session.query(WalletTransaction).where(WalletTransaction.uuid == uuid).options(
        selectinload(WalletTransaction.user)
    ).first()
