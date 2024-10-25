import threading

from fastapi import HTTPException
from sqlalchemy.orm import Session

import db_management.dto
import repos.auction_repo
import repos.user_repo
import services.email_service
import tasks.auction_finished_task
from db_management.models import Product, Auction, Bid
from services.socketio_service import get_socket_manager, SocketManager
from utils.constants import AuctionType, AuctionStatus, UserAccountType


async def place_bid(session: Session, auction_id: int, user_id: int, amount: float) -> None:
    user = repos.user_repo.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    # round the amount to 2 decimal places
    amount = round(amount, 2)

    # lock to prevent bidding simultaneously
    with threading.Lock():
        auction = repos.auction_repo.get_auction_by_id(session, auction_id)
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction not found")

        if auction.auction_type != AuctionType.BID:
            raise HTTPException(status_code=400, detail="This auction is not a bid auction")

        if auction.is_auction_finished:
            raise HTTPException(status_code=400, detail="This auction is not biddable / already finished")

        current_bid_winner = auction.bid.current_bid_winner

        # Validate if user already has an active bid
        # If so, check if user is trying to bid on the same auction
        if repos.auction_repo.is_user_participating_in_different_active_bid(session, auction, user):
            raise HTTPException(status_code=400, detail="You can only bid on one auction at a time")

        # User should have at least the current bid value including the amount he wants to bid
        new_bid_value = auction.bid.current_bid_value + amount
        if user.balance_total < new_bid_value:
            raise HTTPException(status_code=400,
                                detail="Insufficient balance to place bid, it's required to have at least current bid value in your account + your bid value")

        if user.id == auction.seller_id:
            raise HTTPException(status_code=400, detail="You cannot bid on your own auction")

        # check if there are any bids
        if current_bid_winner:
            if user.id == current_bid_winner.id:
                raise HTTPException(status_code=400, detail="You are already the highest bidder")

            # check if winner has been changed
            if current_bid_winner.id != user.id:
                # send notification to the previous winner
                await get_socket_manager().bid_winner_update_action(auction.bid.current_bid_winner_id)

        # real logic
        repos.auction_repo.add_bid_participant(session, auction, user)
        repos.auction_repo.create_bid_history_entry(session, auction, user, amount)
        repos.auction_repo.update_bid_winner(auction, user, new_bid_value)

        # freeze the amount of new total bid price in the user's balance
        repos.user_repo.set_frozen_balance(user, new_bid_value)

        # send notification for all participants online
        await SocketManager.bid_price_update_action(auction_id, new_bid_value)

        # save the transaction
        session.commit()


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

        # send email to the buyer and seller
        services.email_service.send_user_won_auction_email(user, auction)
        services.email_service.send_seller_auction_completed_email(auction.seller.email, user, auction)

        # save the transaction
        session.commit()


def create_auction(session: Session, auction: db_management.dto.CreateAuction, user_id: int) -> None:
    user = repos.user_repo.get_by_id(session, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.account_type != UserAccountType.BUSINESS:
        raise HTTPException(status_code=400, detail="Only business accounts can create auctions")

    product = Product(
        name=auction.product.name,
        description=auction.product.description,
        category_id=auction.product.category_id,
        image_url_1=auction.product.images[0],
        image_url_2=auction.product.images[1] if len(auction.product.images) > 1 else None,
        image_url_3=auction.product.images[2] if len(auction.product.images) > 2 else None
    )
    db_auction = Auction(
        auction_type=auction.auction_type,
        end_date=auction.end_date,
        product=product
    )

    # Set the seller
    db_auction.seller = user

    # Set the price based on the auction type
    if auction.auction_type == AuctionType.BID:
        bid = Bid(
            current_bid_value=auction.price,
        )
        db_auction.bid = bid
    else:
        db_auction.buy_now_price = auction.price

    # real logic
    repos.auction_repo.create_auction(session, db_auction)

    # reload tracked auctions
    tasks.auction_finished_task.reload_tracked_auctions()

    # save the transaction
    session.commit()


def bid_finished(session: Session, auction_id: int) -> None:
    auction = repos.auction_repo.get_full_auction_by_id(session, auction_id)
    if auction is None:
        raise ValueError("Auction not found")

    if auction.auction_type != AuctionType.BID:
        raise ValueError("This auction is not a bid auction")

    if auction.auction_status == AuctionStatus.INACTIVE:
        raise ValueError("This auction is not active")

    buyer = auction.bid.current_bid_winner

    # set up auction buyer
    if auction.auction_type == AuctionType.BID:
        auction.buyer = buyer

    # set up auction as finished
    repos.auction_repo.set_auction_status(auction, AuctionStatus.INACTIVE)

    # deduct the amount from the user's balance
    repos.user_repo.deduct_total_balance(buyer, auction.bid.current_bid_value)

    # send email to the buyer and seller
    services.email_service.send_user_won_auction_email(buyer, auction)
    services.email_service.send_seller_auction_completed_email(auction.seller.email, buyer, auction)

    # save the transaction
    session.commit()


def bid_finished(session: Session, auction_id: int) -> None:
    auction = repos.auction_repo.get_full_auction_by_id(session, auction_id)
    if auction is None:
        raise ValueError("Auction not found")

    if auction.auction_type != AuctionType.BID:
        raise ValueError("This auction is not a bid auction")

    if auction.auction_status == AuctionStatus.INACTIVE:
        raise ValueError("This auction is not active")

    buyer = auction.bid.current_bid_winner

    # set up auction buyer
    if auction.auction_type == AuctionType.BID:
        auction.buyer = buyer

    # set up auction as finished
    repos.auction_repo.set_auction_status(auction, AuctionStatus.INACTIVE)

    # deduct the amount from the user's balance
    repos.user_repo.deduct_total_balance(buyer, auction.bid.current_bid_value)

    # send email to the buyer and seller
    services.email_service.send_user_won_auction_email(buyer, auction)
    services.email_service.send_seller_auction_completed_email(auction.seller.email, buyer, auction)

    # save the transaction
    session.commit()
