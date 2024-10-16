from datetime import datetime
from typing import Annotated, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

import repos.auction_repo
from db_management import dto
from db_management.models import Product
from response_models.auth_responses import validate_jwt
from utils.utils import get_db

router = APIRouter(
    prefix="/auction",
    tags=["auction"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


# todo: add auth
@router.put("", status_code=status.HTTP_201_CREATED)
async def create_auction(db: db_dependency, auction: dto.CreateAuction):
    print(auction.dict())
    try:
        repos.auction_repo.create_auction(auction)
        return {"message": "Product added successfully", "product_id": auction.product.name}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/category", status_code=status.HTTP_201_CREATED)
async def create_category(category: dto.CreateCategory):
    try:
        repos.auction_repo.create_category(category)
        return {"message": "Category added successfully"}
    except HTTPException as e:
        raise e


@router.get("/get", status_code=status.HTTP_200_OK)
async def get_product(db: db_dependency, product_id: int = Query(..., description="The ID of the product to fetch")) \
        -> Dict[str, Any]:
    product = db.query(Product).options(joinedload(Product.seller)).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    product_data = {
        "name": product.name,
        "description": product.description,
        "price": product.price,
        "status": product.status,
        "category_id": product.category_id,
        "image_url_1": product.image_url_1,
        "image_url_2": product.image_url_2,
        "image_url_3": product.image_url_3,
        "quantity": product.quantity,
        "end_date": product.end_date,
        "isBid": product.isBid,
        "buyer_id": product.buyer_id,
        "seller": {
            "id": product.seller.id,
            "username": product.seller.username,
            "email": product.seller.email,
            "profile_image_url": product.seller.profile_image_url
        },
    }

    return {"product": product_data}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_product(
        product_id: int = Query(..., description="The ID of the product to delete"),
        db: Session = Depends(db_dependency),
        user: dict = Depends(user_dependency)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        if user['id'] != product.seller_id and user['role'] != "admin":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")

        db.delete(product)
        db.commit()

        return {"detail": "Product deleted successfully"}

    except HTTPException as http_exc:
        raise http_exc

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail="An error occurred while deleting the product") from e


@router.get("/fetch/last", status_code=status.HTTP_200_OK)
async def get_last_products(db: Session = Depends(get_db)):
    products = (
        db.query(Product)
        .options(joinedload(Product.category))
        .options(joinedload(Product.seller))
        .order_by(Product.created_at.desc())
        .limit(5)
        .all()
    )

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


@router.get("/by-category/{category_id}", status_code=status.HTTP_200_OK)
async def get_product_by_category(
        db: db_dependency,
        category_id: int,
        skip: int = Query(0, description="Number of products to skip"),
        limit: int = Query(10, description="Number of products to return")
) -> Dict[str, Any]:
    products = db.query(Product) \
        .filter(Product.category_id == category_id) \
        .order_by(Product.created_at.desc()) \
        .offset(skip) \
        .limit(limit) \
        .all()

    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No products found for this category")

    product_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": product.price,
            "status": product.status,
            "image_url_1": product.image_url_1,
            "quantity": product.quantity,
            "end_date": product.end_date,
            "isBid": product.isBid,
            "seller_id": product.seller_id
        }
        product_list.append(product_data)

    return {"products": product_list}
