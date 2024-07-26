from datetime import date, datetime
from typing import Annotated, Optional, Dict, Any

import cloudinary.uploader

from response_models.product_responses import ProductGetResponse

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, Form, File
from sqlalchemy.orm import Session, joinedload

from db_management.models import Product, User

from utils.utils import get_db, validate_image
from response_models.auth_responses import validate_jwt

router = APIRouter(
    prefix="/product",
    tags=["product"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_product(
    db: db_dependency,
    user: user_dependency,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    quantity: int = Form(...),
    category_id: int = Form(...),
    end_date: int = Form(...),
    image1: UploadFile = File(...),
    image2: UploadFile = File(...),
    image3: UploadFile = File(...),
    status: Optional[str] = Form("active")
):
    try:
        validate_image(image1)
        validate_image(image2)
        validate_image(image3)

        result_image1 = cloudinary.uploader.upload(image1.file)
        result_image2 = cloudinary.uploader.upload(image2.file)
        result_image3 = cloudinary.uploader.upload(image3.file)

        image_url_1 = result_image1.get('url')
        image_url_2 = result_image2.get('url')
        image_url_3 = result_image3.get('url')

        end_date_datetime = datetime.fromtimestamp(end_date / 1000)

        db_product = Product(
            name=name,
            description=description,
            price=price,
            status=status,
            quantity=quantity,
            end_date=end_date_datetime,
            seller_id=user['id'],
            category_id=category_id,
            image_url_1=image_url_1,
            image_url_2=image_url_2,
            image_url_3=image_url_3,
            created_at=datetime.now()
        )
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return {"message": "Product added successfully", "product_id": db_product.id}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get", status_code=status.HTTP_200_OK)
async def get_product(db: db_dependency, product_id: int = Query(..., description="The ID of the product to fetch"))\
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
        "buyer_id": product.buyer_id,
        "seller": {
            "id": product.seller.id,
            "username": product.seller.username,
            "email": product.seller.email,
            "profile_image_url": product.seller.profile_image_url
        },
    }

    return {"product": product_data}


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
    products = db.query(Product)\
        .filter(Product.category_id == category_id)\
        .order_by(Product.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
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
            "seller_id": product.seller_id
        }
        product_list.append(product_data)

    return {"products": product_list}