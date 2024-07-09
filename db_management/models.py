from sqlalchemy.orm import relationship

from db_management.database import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id'), nullable=False)
    address = relationship('Address')
    profile_image_url = Column(String(255), nullable=True)

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


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)
    price = Column(DECIMAL, nullable=False)
    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category')
    status = Column(String(255), nullable=False)
    quantity = Column(Integer, nullable=False)
    end_date = Column(DateTime, nullable=False)
    seller_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    seller = relationship('User', foreign_keys=[seller_id])
    buyer_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    buyer = relationship('User', foreign_keys=[buyer_id])
    image_url_1 = Column(String(255), nullable=True)
    image_url_2 = Column(String(255), nullable=True)
    image_url_3 = Column(String(255), nullable=True)