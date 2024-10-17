import threading

from fastapi import HTTPException

import repos.auction_repo
import repos.user_repo
from db_management.models import Auction, User


def place_bid(auction: Auction, user: User, amount: float) -> None:
    with threading.Lock():  # lock to prevent bidding simultaneously
        if not auction.is_biddable:
            raise HTTPException(status_code=400, detail="This auction is not biddable / already finished")

        if user.get_current_balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient balance to place bid")

        if user.id == auction.seller_id:
            raise HTTPException(status_code=400, detail="You cannot bid on your own auction")

        if user.id == auction.buyer_id:
            raise HTTPException(status_code=400, detail="You are already the highest bidder")

        if amount <= auction.bid.current_bid_value:
            raise HTTPException(status_code=400, detail="Bid value should be higher than the current bid")

        # real logic
        repos.auction_repo.add_bid_participant(auction, user)
        repos.auction_repo.create_bid_history_entry(auction, user, amount)
        repos.auction_repo.update_bid_winner(auction, user, amount)

        # deduct the amount from the user's balance
        repos.user_repo.increase_frozen_balance(user, amount)
