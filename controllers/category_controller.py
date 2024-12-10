from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
from db_management import dto
from db_management.database import get_db
from response_models.auth_responses import validate_auth_jwt

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Depends(validate_auth_jwt)


@router.get("/id/{category_id}", status_code=status.HTTP_200_OK)
async def get_category(category_id: int, db: db_dependency):
    category = repos.auction_repo.get_category_by_id(db, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category.to_public()


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency):
    categories = repos.auction_repo.get_categories(db)
    return {"categories": [category.to_public() for category in categories]}


@router.put("", status_code=status.HTTP_201_CREATED)
async def create_category(category: dto.CreateCategory, db: db_dependency):
    if not repos.auction_repo.create_category(db, category):
        raise HTTPException(status_code=400, detail="Category already exists")
    return {"message": "Category added successfully"}


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_category(dto: dto.DeleteCategory, db: db_dependency):
    if not repos.auction_repo.delete_category(db, dto.category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}
