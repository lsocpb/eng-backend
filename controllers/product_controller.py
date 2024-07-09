from datetime import date, datetime
from typing import Annotated, Optional

import cloudinary.uploader

from response_models.product_responses import ProductAddResponse

from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, Form, File
from sqlalchemy.orm import Session

from db_management.models import Product

from utils.utils import get_db
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
        image_url_3=image_url_3
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return {"message": "Product added successfully"}
