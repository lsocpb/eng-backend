from database import Base
from sqlalchemy import Column, Integer, String, DateTime



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    