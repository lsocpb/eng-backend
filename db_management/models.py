from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, DECIMAL
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from db_management.database import Base
from utils.constants import *


class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False)
    description = Column(String(255), nullable=False)
    status = Column(String(255), nullable=False)
    icon = Column(String(255), nullable=True)


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

    category_id = Column(Integer, ForeignKey('category.id'), nullable=False)
    category = relationship('Category')

    image_url_1 = Column(String(255), nullable=True)
    image_url_2 = Column(String(255), nullable=True)
    image_url_3 = Column(String(255), nullable=True)


class Bid(Base):
    __tablename__ = 'bid'

    id = Column(Integer, primary_key=True, index=True)

    current_bid_value = Column(DECIMAL, nullable=False)

    current_bid_winner_id = Column(Integer, ForeignKey('user.id'), nullable=False)
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

    created_at = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)

    bid_id = Column(Integer, ForeignKey('bid.id'), nullable=True)
    bid = relationship('Bid')

    buy_now_price = Column(DECIMAL, nullable=True)

    seller_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    seller = relationship('User')
    buyer_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    buyer = relationship('User', foreign_keys=[buyer_id], back_populates='products_bought')

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


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    role = Column(SQLAlchemyEnum(UserRole), default=UserRole.USER, nullable=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False)
    address_id = Column(Integer, ForeignKey('address.id'), nullable=False)
    address = relationship('Address')
    profile_image_url = Column(String(255), nullable=True)

    balance_available = Column(DECIMAL, nullable=False, default=0.0)  # Available balance for withdraw / buy now
    balance_reserved = Column(DECIMAL, nullable=False, default=0.0)  # Balance reserved for bids / frozen

    products_sold = relationship('Product', foreign_keys=[Auction.seller_id], back_populates='seller')
    products_bought = relationship('Product', foreign_keys=[Auction.buyer_id], back_populates='buyer')

    @hybrid_property
    def get_current_balance(self) -> float:
        if self.balance_available - self.balance_reserved < 0:
            return 0.0

        return self.balance_available - self.balance_reserved
