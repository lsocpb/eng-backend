from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, FLOAT
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
        return f"Category: [name: {self.name} desc: {self.description}]"

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "icon": self.icon
        }


class Address(Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True, index=True)
    street = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    zip = Column(String(255), nullable=False)

    def __str__(self):
        return f"[Address: {self.street} {self.city} {self.zip}]"


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
        return f"Product: [name: {self.name} desc: {self.description}]"

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category_id": self.category.id,
            "image_url_1": self.image_url_1,
            "image_url_2": self.image_url_2,
            "image_url_3": self.image_url_3
        }


class Bid(Base):
    __tablename__ = 'bid'

    id = Column(Integer, primary_key=True, index=True)

    current_bid_value = Column(FLOAT, nullable=False)

    current_bid_winner_id = Column(Integer, ForeignKey('user.id'))
    current_bid_winner = relationship('User')
    bidders = relationship('BidParticipant', back_populates='bid')  # Store all bidders

    def __str__(self):
        return f"Bid: [current_bid: {self.current_bid_value}]"

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "current_bid_value": self.current_bid_value,
            "current_bid_winner": self.current_bid_winner.to_public() if self.current_bid_winner else None,
            "bidders": [b.user.to_public() for b in self.bidders]
        }


class BidParticipant(Base):
    __tablename__ = 'bid_participant'

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=False)
    bid = relationship('Bid')

    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')

    created_at = Column(DateTime, nullable=False, default=datetime.now)  # When the user placed the bid


class BidHistory(Base):
    __tablename__ = 'bid_history'

    id = Column(Integer, primary_key=True, index=True)
    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=False)
    bid = relationship('Bid')
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    user = relationship('User')

    amount = Column(FLOAT, nullable=False)  # Exact amount the user bid
    created_at = Column(DateTime, nullable=False, default=datetime.now)  # When the user placed the bid


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

    buy_now_price = Column(FLOAT, nullable=True)

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

    @hybrid_property
    def is_biddable(self) -> bool:
        if self.auction_type == AuctionType.BUY_NOW:
            return False

        if self.is_auction_finished:
            return False

        return True

    def __str__(self):
        return f"Auction: [{self.product.name} - {self.product.description} started: {self.created_at} ends: {self.end_date}]"

    def to_public(self) -> dict:
        d = {
            "id": self.id,
            "category": self.product.category.to_public(),
            "auction_type": self.auction_type,
            "quantity": self.quantity,
            "product": self.product.to_public(),
            "created_at": self.created_at,
            "end_date": self.end_date,
            "seller": self.seller.to_public_detailed(),
            "buyer": self.buyer.to_public() if self.buyer else None,
            "is_auction_finished": self.is_auction_finished,
            "is_new": (datetime.now() - self.created_at).days < 7,
            "days_left": (self.end_date - datetime.now()).days,
        }

        if self.auction_type == AuctionType.BID:
            d["bid"] = self.bid.to_public()
            d["price"] = self.bid.current_bid_value
        else:
            d["price"] = self.buy_now_price

        return d


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

    balance_total = Column(FLOAT, nullable=False, default=0.0)  # Available balance for withdraw / buy now
    balance_reserved = Column(FLOAT, nullable=False, default=0.0)  # Balance reserved for bids / frozen

    products_sold: Mapped[List["Auction"]] = relationship(back_populates="seller", foreign_keys=[Auction.seller_id])
    products_bought: Mapped[List["Auction"]] = relationship(back_populates="buyer", foreign_keys=[Auction.buyer_id])

    @hybrid_property
    def get_current_balance(self) -> float:
        if self.balance_total - self.balance_reserved < 0:
            return 0.0

        return self.balance_total - self.balance_reserved

    def __str__(self):
        return f"User: [{self.username} - {self.email} | total, available, reserved: {self.balance_total}, {self.get_current_balance}, {self.balance_reserved}]"

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "profile_image_url": self.profile_image_url,
        }

    def to_public_detailed(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_image_url": self.profile_image_url,
            "last_login_date": self.last_login_date
        }
