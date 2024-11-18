from datetime import datetime
from typing import List

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, FLOAT, func
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship, mapped_column, Mapped, declared_attr

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


class Billing(Base):
    __tablename__ = 'billing'
    id = Column(Integer, primary_key=True)
    billing_type = Column(String(50))

    # Polymorphic discriminator
    @declared_attr
    def __mapper_args__(self):
        return {
            'polymorphic_identity': 'billing',
            'polymorphic_on': self.billing_type
        }


class UserBilling(Billing):
    __tablename__ = 'user_billing'
    id = Column(Integer, ForeignKey('billing.id'), primary_key=True)
    first_name = Column(String(255), nullable=False)
    last_name = Column(String(255), nullable=False)
    address = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)

    def to_private(self) -> dict:
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
            "phone_number": self.phone_number,
        }

    def __str__(self):
        return f"UserBilling: [details: {self.address} {self.postal_code} {self.city} {self.country}]"

    __mapper_args__ = {
        'polymorphic_identity': 'user_billing',
    }


class CompanyBilling(Billing):
    __tablename__ = 'company_billing'
    id = Column(Integer, ForeignKey('billing.id'), primary_key=True)
    name = Column(String(255), nullable=False)
    tax_id = Column(String(255), nullable=False)  # NIP
    address = Column(String(255), nullable=False)
    postal_code = Column(String(255), nullable=False)
    city = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    country = Column(String(255), nullable=False)
    phone_number = Column(String(255), nullable=False)
    bank_account = Column(String(255), nullable=False)

    def to_private(self) -> dict:
        return {
            "id": self.id,
            "company_name": self.name,
            "tax_id": self.tax_id,
            "address": self.address,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
            "phone_number": self.phone_number,
            "bank_account": self.bank_account
        }

    def __str__(self):
        return f"CompanyBilling: [name: {self.name} address: {self.address} {self.postal_code} {self.city} {self.country}]"

    __mapper_args__ = {
        'polymorphic_identity': 'company_billing',
    }


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
    auction_status = Column(SQLAlchemyEnum(AuctionStatus), nullable=False, default=AuctionStatus.ACTIVE)

    product_id = Column(Integer, ForeignKey('product.id'), nullable=False)
    product = relationship('Product')

    created_at = Column(DateTime, nullable=False, default=datetime.now)
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

        if self.auction_status != AuctionStatus.ACTIVE:
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
        return f"Auction: [{self.product.name} - {self.product.description} started: {self.created_at} ends: {self.end_date}]"

    def to_public(self) -> dict:
        d = {
            "id": self.id,
            "category": self.product.category.to_public(),
            "auction_type": self.auction_type,
            "product": self.product.to_public(),
            "created_at": self.created_at,
            "end_date": self.end_date,
            "seller": self.seller.to_public_detailed(),
            "buyer": self.buyer.to_public() if self.buyer else None,
            "is_auction_finished": self.is_auction_finished,
            "is_new": (datetime.now() - self.created_at).days < 7,
        }

        if self.is_auction_finished:
            d["days_left"] = 0
        else:
            d["days_left"] = (self.end_date - datetime.now()).days

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
    account_type = Column(SQLAlchemyEnum(UserAccountType), default=UserAccountType.PERSONAL, nullable=True)
    password_hash = Column(String(255), nullable=False)
    username = Column(String(255), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    last_login_date = Column(DateTime, nullable=False, default=datetime.now, server_default=func.now())
    created_at = Column(DateTime, nullable=False, default=datetime.now, server_default=func.now())
    wallet_transactions: Mapped[List["WalletTransaction"]] = relationship("WalletTransaction", back_populates="user")

    billing_details_id = Column(Integer, ForeignKey('billing.id'))
    billing_details: Mapped["Billing"] = relationship("Billing", backref="user")

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

    def to_private(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "profile_image_url": self.profile_image_url,
            "last_login_date": self.last_login_date,
            "role": self.role,
            "account_type": self.account_type,
            "billing": self.billing_details.to_private(),
            "balance_total": self.balance_total,
            "balance_reserved": self.balance_reserved,
        }


class WalletTransaction(Base):
    __tablename__ = 'wallet_transaction'

    id = Column(Integer, primary_key=True, index=True)
    uuid = Column(String(255), nullable=False)
    stripe_payment_intent_id = Column(String(255), nullable=True)
    stripe_checkout_session_id = Column(String(255), nullable=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('user.id'), nullable=False)
    user: Mapped["User"] = relationship('User')

    amount = Column(FLOAT, nullable=False)
    transaction_status = Column(SQLAlchemyEnum(TransactionStatus), nullable=False, default=TransactionStatus.PENDING)
    created_at = Column(DateTime, nullable=False, default=datetime.now)
    receipt_url = Column(String(255), nullable=True)

    def __str__(self):
        return f"WalletTransaction: [{self.user.username} - {self.amount} - {self.transaction_type}]"

    def to_public(self) -> dict:
        return {
            "id": self.id,
            "uuid": self.uuid,
            "created_at": self.created_at,
            "amount": self.amount,
            "transaction_status": self.transaction_status,
            "receipt_url": self.receipt_url,
            "stripe_payment_id": self.stripe_payment_intent_id,
        }
