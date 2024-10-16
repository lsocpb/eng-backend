import os
from typing import Any
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

load_dotenv()
DB_URL = os.getenv("DB_URL")

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True, pool_recycle=3600)  # reconect after 1 hour
session_maker = sessionmaker(bind=engine, expire_on_commit=False)


def create_db() -> None:
    """
    Creates the database tables by calling `Base.metadata.create_all(engine)`.
    """
    Base.metadata.create_all(engine)


def get_db() -> Generator[Session, Any, None]:
    """
    Returns a generator that yields a SQLAlchemy session. This session should be used for all database interactions within the current request context.
    """
    with session_maker() as session:
        yield session


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
