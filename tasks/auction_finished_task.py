import threading
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler

import repos.auction_repo
import services.auction_service
from db_management.database import session_maker
from utils.constants import fastapi_logger as logger, AuctionType, AuctionStatus

# Task to check if an auction has ended
tracked_auctions = {}  # <auction_id>: <end_time>
lock = threading.Lock()


# reload all tracked auctions
def reload_tracked_auctions():
    with lock:
        with session_maker() as session:
            auctions = repos.auction_repo.get_all_auctions(session)
            for auction in auctions:
                if auction.auction_type == AuctionType.BUY_NOW:
                    continue
                if not auction.auction_status == AuctionStatus.ACTIVE:
                    continue

                tracked_auctions[auction.id] = auction.end_date
            logger.trace(f"Reloaded {len(tracked_auctions)} tracked auctions")


def check_auctions():
    # prevent checking if auctions are reloading
    with lock:
        for auction_id in list(tracked_auctions.keys()):
            logger.trace(
                f"Checking auction {auction_id} it expires at {tracked_auctions[auction_id]} (left: {tracked_auctions[auction_id] - datetime.now()})")
            if tracked_auctions[auction_id] <= datetime.now():
                logger.info(f"Auction {auction_id} has ended")
                with session_maker() as session:
                    services.auction_service.bid_finished(session, auction_id)
                del tracked_auctions[auction_id]


scheduler = BackgroundScheduler()
scheduler.add_job(check_auctions, 'interval', seconds=60)  # Check every minute
