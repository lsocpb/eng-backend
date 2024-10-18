import sys
from enum import Enum

from loguru import logger

DOMAIN_BASE = "https://charfair.me"
STRIPE_LISTENING_EVENTS = ['charge.succeeded', 'payment_intent.succeeded', 'payment_intent.created']


class WebSocketAction(str, Enum):
    BID_PRICE_UPDATE = 'bid_price_update'
    BID_WINNER_UPDATE = 'bid_winner_update'


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


def initialize_logger():
    # Usuń domyślne wyjście do konsoli, aby uniknąć duplikatów
    logger.remove()

    # SocketIO log console
    logger.add(
        sys.stdout,  # Konsola
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <red>|</red> <cyan>{level: <5}</cyan> <red>|</red> <blue>SOCKET.IO</blue> <red>|</red> {message}",
        level="INFO",
        filter=lambda record: "SOCKETIO" in record["extra"],
        colorize=True
    )

    # SocketIO log file
    logger.add(
        "logs/socketio.log",  # Plik
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <5} | {message}",
        level="TRACE",
        filter=lambda record: "SOCKETIO" in record["extra"]
    )

    # FastAPI log console
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <red>|</red> <cyan>{level: <5}</cyan> <red>|</red> <blue>FASTAPI</blue> <red>|</red> {message}",
        level="INFO",
        filter=lambda record: "FASTAPI" in record["extra"],
        colorize=True
    )

    # FastAPI log file
    logger.add(
        "logs/fastapi.log",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <5} | {message}",
        level="TRACE",
        filter=lambda record: "FASTAPI" in record["extra"]
    )


initialize_logger()

# Stworzenie oddzielnych loggerów
socketio_logger = logger.bind(SOCKETIO=True)
fastapi_logger = logger.bind(FASTAPI=True)
