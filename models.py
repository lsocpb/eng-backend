from sqlalchemy.orm import relationship

from database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id'), nullable=False)
    address = relationship('Address')

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip = Column(String(255), nullable=False)