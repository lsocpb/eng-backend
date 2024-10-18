import sys
from enum import Enum

from loguru import logger

DOMAIN_BASE = "https://charfair.me"
STRIPE_LISTENING_EVENTS = ['charge.succeeded', 'payment_intent.succeeded', 'payment_intent.created']


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

    # Logowanie do konsoli (sys.stdout) z poziomem INFO
    # Dodanie logowania do konsoli dla SOCKETIO
    logger.add(
        sys.stdout,  # Konsola
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <red>|</red> <cyan>{level: <5}</cyan> <red>|</red> <blue>SOCKET.IO</blue> <red>|</red> {message}",
        level="INFO",
        filter=lambda record: "SOCKETIO" in record["extra"],
        colorize=True
    )

    # Dodanie logowania do pliku dla SOCKETIO
    logger.add(
        "/logs/socketio.log",  # Plik
        format="{time} | {level: <5} | {message}",
        level="INFO",
        filter=lambda record: "SOCKETIO" in record["extra"]
    )

    # Dodanie logowania do konsoli dla FASTAPI
    logger.add(
        sys.stdout,  # Konsola
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <red>|</red> <cyan>{level: <5}</cyan> <red>|</red> <blue>FASTAPI</blue> <red>|</red> {message}",
        level="INFO",
        filter=lambda record: "FASTAPI" in record["extra"],
        colorize=True
    )

    # Dodanie logowania do pliku dla FASTAPI
    logger.add(
        "/logs/fastapi.log",  # Plik
        format="{time} | {level: <5} | {message}",
        level="INFO",
        filter=lambda record: "FASTAPI" in record["extra"]
    )


initialize_logger()

# Stworzenie oddzielnych loggerów
socketio_logger = logger.bind(SOCKETIO=True)
fastapi_logger = logger.bind(FASTAPI=True)
