from enum import Enum


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'


class AuctionType(str, Enum):
    BUY_NOW = 'buy_now'
    BID = 'bid'


class AuctionStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELLED = 'cancelled'
