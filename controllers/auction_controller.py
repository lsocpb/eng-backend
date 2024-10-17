from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
import services.purcharse_service
from db_management import dto
from db_management.database import get_db
from db_management.dto import PlaceBid
from response_models.auth_responses import validate_jwt

router = APIRouter(
    prefix="/auction",
    tags=["auction"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


@router.get("/{auction_id}", status_code=status.HTTP_200_OK)
async def get_auction(auction_id: str, db: db_dependency):
    if auction_id == "last":
        products = repos.auction_repo.get_latest_auctions(db, 5)
        return {"products": [product.to_public() for product in products]}
    elif auction_id.isnumeric():
        auction = repos.auction_repo.get_full_auction_by_id(db, int(auction_id))
        if auction is None:
            raise HTTPException(status_code=404, detail="Auction not found")

        return auction.to_public()

    else:
        raise HTTPException(status_code=400, detail="Invalid auction id")


# todo: add auth
@router.put("", status_code=status.HTTP_201_CREATED)
async def create_auction(auction: dto.CreateAuction, db: db_dependency):
    user = repos.user_repo.get_by_id(db, auction.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    repos.auction_repo.create_auction(db, auction, user)


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_auction(dto: dto.DeleteAuction, db: db_dependency):
    repos.auction_repo.delete_auction(db, dto.auction_id)
    return {"message": "Auction deleted successfully"}


@router.post("/bid", status_code=status.HTTP_200_OK)
async def place_bid(dto: PlaceBid, user: user_dependency, db: db_dependency):
    services.purcharse_service.place_bid(db, dto.auction_id, user['id'], dto.bid_value)
    return {"message": "Bid placed successfully"}


@router.post("/buy_now", status_code=status.HTTP_200_OK)
async def buy_now(dto: dto.BuyNow, user: user_dependency, db: db_dependency):
    services.purcharse_service.buy_now(db, dto.auction_id, user['id'])
    return {"message": "Product bought successfully"}


@router.get("/category/{category_id}", status_code=status.HTTP_200_OK)
async def get_auctions_by_category(category_id: int, db: db_dependency):
    auctions = repos.auction_repo.get_auction_list_by_category(db, category_id)
    if not auctions:
        raise HTTPException(status_code=404, detail="No auctions found")
    return {"auctions": [auction.to_public() for auction in auctions]}
