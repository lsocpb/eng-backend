from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
import services.bid_service
from db_management import dto
from db_management.dto import PlaceBid
from response_models.auth_responses import validate_jwt
from utils.utils import get_db

router = APIRouter(
    prefix="/auction",
    tags=["auction"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


@router.get("/{auction_id}", status_code=status.HTTP_200_OK)
async def get_auction(auction_id: int):
    auction = repos.auction_repo.get_full_auction_by_id(auction_id)
    if auction is None:
        raise HTTPException(status_code=404, detail="Auction not found")

    return auction.to_public()


# todo: add auth
@router.put("", status_code=status.HTTP_201_CREATED)
async def create_auction(auction: dto.CreateAuction):
    try:
        repos.auction_repo.create_auction(auction)
        return {"message": "Product added successfully", "product_id": auction.product.name}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_auction(dto: dto.DeleteAuction):
    repos.auction_repo.delete_auction(dto.auction_id)
    return {"message": "Auction deleted successfully"}


@router.get("/last", status_code=status.HTTP_200_OK)
async def get_last_auctions():
    products = repos.auction_repo.get_latest_auctions(5)

    result = []
    for product in products:
        days_left = (product.end_date - datetime.now()).days

        result.append({
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),
            "image_url_1": product.image_url_1,
            "category_id": product.category_id,
            "category_name": product.category.name if product.category else None,
            "seller_name": product.seller.username if product.seller else "Anonymous",
            "seller_avatar": product.seller.profile_image_url if product.seller else None,
            "bid_count": product.quantity,
            "days_left": max(days_left, 0),
            "is_new": (datetime.now() - product.created_at).days < 7,
            "isBid": product.isBid,
            "status": product.status
        })

    return {"products": result}


@router.post("/bid", status_code=status.HTTP_200_OK)
async def place_bid(dto: PlaceBid, user: dict = Depends(user_dependency)):
    try:
        services.bid_service.place_bid(dto.auction_id, user['id'], dto.bid_value)
        return {"message": "Bid placed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/category/{category_id}", status_code=status.HTTP_200_OK)
async def get_auctions_by_category(category_id: int):
    auctions = repos.auction_repo.get_auctions_by_category(category_id)
    if not auctions:
        raise HTTPException(status_code=404, detail="No auctions found")
    return {"auctions": [auction.to_public() for auction in auctions]}
