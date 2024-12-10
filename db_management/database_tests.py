import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_management.database import Base, get_db
from main import app

load_dotenv()
DB_URL = os.getenv("TEST_DB_URL")

engine = create_engine(DB_URL, echo=False, pool_pre_ping=True, pool_recycle=3600,
                       isolation_level="AUTOCOMMIT")  # reconect after 1 hour
session_maker = sessionmaker(bind=engine, expire_on_commit=False)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db
print("Test database connection established")
