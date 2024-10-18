from enum import Enum

DOMAIN_BASE = "https://charfair.me"


class TransactionStatus(str, Enum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'
    EXPIRED = 'expired'


class UserRole(str, Enum):
    ADMIN = 'admin'
    USER = 'user'


class UserAccountType(str, Enum):
    PERSONAL = 'personal'
    BUSINESS = 'business'
    BUSINESS_UNVERIFIED = 'business_unverified'


class AuctionType(str, Enum):
    BUY_NOW = 'buy_now'
    BID = 'bid'


class AuctionStatus(str, Enum):
    ACTIVE = 'active'
    INACTIVE = 'inactive'
    CANCELLED = 'cancelled'
