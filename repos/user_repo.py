from sqlalchemy import Update, Delete
from sqlalchemy.orm import selectinload
from sqlalchemy.sql.functions import current_timestamp

from db_management.database import session_maker
from db_management.models import User


def get_by_id(user_id: int) -> User | None:
    with session_maker() as session:
        return session.query(User).options(
            selectinload(User.address)  # load the address relationship
        ).all()[0]


def delete(user_id: int) -> None:
    with session_maker.begin() as session:
        session.execute(Delete(User).where(User.id == user_id))


def update_user_profile_image(id: int, profile_image_url: str) -> None:
    with session_maker.begin() as session:
        session.execute(Update(User).where(User.id == id).values({
            User.profile_image_url: profile_image_url,
            User.updated_at: current_timestamp()
        }))


def tests():
    from db_management.database import create_db

    create_db()

    user = get_by_id(user_id=3)
    print(user.email, user.profile_image_url, user.username, user.address.zip)


tests()
