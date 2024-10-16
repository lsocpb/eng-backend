from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, mapped_column, Mapped

from db_management.database import Base
from utils.constants import *


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)

    def __str__(self):
        return f"Category: {self.name} - {self.description}"


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip = Column(String(255), nullable=False)

    def __str__(self):
        return f"Address: {self.street} - {self.city} - {self.zip}"


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(String(255), nullable=False)

    category_id: Mapped[int] = mapped_column(ForeignKey("category.id"), nullable=False)
    category: Mapped["Category"] = relationship()

    image_url_1 = Column(String(255), nullable=True)
    image_url_2 = Column(String(255), nullable=True)
    image_url_3 = Column(String(255), nullable=True)

    def __str__(self):
        return f"Product: {self.name} - {self.description}"


class Bid(Base):
    __tablename__ = 'bid'

    id = Column(Integer, primary_key=True, index=True)

    current_bid_value = Column(DECIMAL, nullable=False)

    current_bid_winner_id = Column(Integer, ForeignKey('user.id'))
    current_bid_winner = relationship('User')
    bidders = relationship('BidParticipant', back_populates='bid')  # Store all bidders


class BidParticipant(Base):
    __tablename__ = 'bid_participant'

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=False)
    bid = relationship('Bid')

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')

    created_at = Column(DateTime, nullable=False)  # When the user joined the bid


class BidHistory(Base):
    __tablename__ = 'bid_history'

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=False)
    bid = relationship('Bid')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')

    amount = Column(DECIMAL, nullable=False)  # Exact amount the user bid
    created_at = Column(DateTime, nullable=False)  # When the user placed the bid


class Auction(Base):
    __tablename__ = 'auction'

    id = Column(Integer, primary_key=True, index=True)
    auction_type = Column(SQLAlchemyEnum(AuctionType), nullable=False)
    quantity = Column(Integer, nullable=False)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')

    created_at = Column(DateTime(timezone=True), default=datetime.now, nullable=False)
    end_date = Column(DateTime, nullable=False)

    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=True)
    bid = relationship('Bid')

    buy_now_price = Column(DECIMAL, nullable=True)

    seller_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    seller: Mapped["User"] = relationship(back_populates="products_sold", foreign_keys=[seller_id])

    buyer_id: Mapped[int] = mapped_column(ForeignKey("user.id"), nullable=True)
    buyer: Mapped["User"] = relationship(back_populates="products_bought", foreign_keys=[buyer_id])

    @hybrid_property
    def is_auction_finished(self) -> bool:
        # Auction is finished if just expired
        if self.end_date < datetime.now():
            return True

        # Auction is finished if buyer is set in buy now auction
        if self.auction_type == AuctionType.BUY_NOW:
            return self.buyer is not None

        return False

    @hybrid_property
    def get_buyer(self):
        if self.auction_type == AuctionType.BUY_NOW:
            return self.buyer
        else:
            return self.bid.current_bid_winner

    def __str__(self):
        return f"Auction: {self.product.name} - {self.product.description} started at {self.created_at} and ends at {self.end_date}"


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)

    address_id: Mapped[int] = mapped_column(ForeignKey("address.id"), nullable=False)
    address: Mapped["Address"] = relationship()

    profile_image_url = Column(String(255), nullable=True)

    balance_available = Column(DECIMAL, nullable=False, default=0.0)  # Available balance for withdraw / buy now
    balance_reserved = Column(DECIMAL, nullable=False, default=0.0)  # Balance reserved for bids / frozen

    products_sold: Mapped[List["Auction"]] = relationship(back_populates="seller", foreign_keys=[Auction.seller_id])
    products_bought: Mapped[List["Auction"]] = relationship(back_populates="buyer", foreign_keys=[Auction.buyer_id])

    @hybrid_property
    def get_current_balance(self) -> float:
        if self.balance_available - self.balance_reserved < 0:
            return 0.0

        return self.balance_available - self.balance_reserved

    def __str__(self):
        return f"User: {self.username} - {self.email}"
