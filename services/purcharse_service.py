import threading

from fastapi import HTTPException
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
from utils.constants import AuctionType, AuctionStatus


def place_bid(session: Session, auction_id: int, user_id: int, amount: float) -> None:
    user = repos.user_repo.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # round the amount to 2 decimal places
    amount = round(amount, 2)

    with threading.Lock():  # lock to prevent bidding simultaneously
        auction = repos.auction_repo.get_auction_by_id(session, auction_id)
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction not found")

        if auction.auction_type != AuctionType.BID:
            raise HTTPException(status_code=400, detail="This auction is not a bid auction")

        if auction.is_auction_finished:
            raise HTTPException(status_code=400, detail="This auction is not biddable / already finished")

        # Validate if user already has an active bid
        # If so, check if user is trying to bid on the same auction
        user_bidder_auction_id = repos.auction_repo.get_user_active_bid_participant(session, user_id=user.id)
        if user_bidder_auction_id != 0 and user_bidder_auction_id != auction.id:
            raise HTTPException(status_code=400, detail="You can only bid on one auction at a time")

        # User should have at least the current bid value including the amount he wants to bid
        new_bid_value = auction.bid.current_bid_value + amount
        if user.balance_total < new_bid_value:
            raise HTTPException(status_code=400,
                                detail="Insufficient balance to place bid, it's required to have at least current bid value in your account + your bid value")

        if user.id == auction.seller_id:
            raise HTTPException(status_code=400, detail="You cannot bid on your own auction")

        if user.id == auction.buyer_id:
            raise HTTPException(status_code=400, detail="You are already the highest bidder")

        # real logic
        repos.auction_repo.add_bid_participant(session, auction, user)
        repos.auction_repo.create_bid_history_entry(session, auction, user, amount)
        repos.auction_repo.update_bid_winner(session, auction, user, new_bid_value)

        # freeze the amount of new total bid price in the user's balance
        repos.user_repo.set_frozen_balance(session, user, new_bid_value)


def buy_now(session: Session, auction_id: int, user_id: int) -> None:
    user = repos.user_repo.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    with threading.Lock():  # lock to prevent buying simultaneously
        auction = repos.auction_repo.get_full_auction_by_id(session, auction_id)
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction not found")

        if auction.auction_type != AuctionType.BUY_NOW:
            raise HTTPException(status_code=400, detail="This auction is not a buy now auction")

        if auction.is_auction_finished:
            raise HTTPException(status_code=400, detail="This auction has already finished")

        if user.get_current_balance < auction.buy_now_price:
            raise HTTPException(status_code=400, detail="Insufficient balance to buy now")

        if user.id == auction.seller_id:
            raise HTTPException(status_code=400, detail="You cannot buy your own auction")

        # real logic
        repos.auction_repo.add_user_auction_buyer(auction, user)
        repos.auction_repo.set_auction_status(auction, AuctionStatus.INACTIVE)

        # deduct the amount from the user's balance
        repos.user_repo.deduct_total_balance(user, auction.buy_now_price)

        # save the transaction
        session.commit()
