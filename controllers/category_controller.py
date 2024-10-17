from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
from db_management import dto
from response_models.auth_responses import validate_jwt
from utils.utils import get_db

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Depends(validate_jwt)


@router.put("", status_code=status.HTTP_201_CREATED)
async def create_category(category: dto.CreateCategory):
    try:
        repos.auction_repo.create_category(category)
        return {"message": "Category added successfully"}
    except HTTPException as e:
        raise e


@router.get("", status_code=status.HTTP_200_OK)
async def get_category(dto: dto.GetCategory):
    category = repos.auction_repo.get_category_by_id(dto.category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    return category.to_public()


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_category(dto: dto.DeleteCategory):
    repos.auction_repo.delete_category(dto.category_id)
    return {"message": "Category deleted successfully"}


@router.get("/all", status_code=status.HTTP_200_OK)
async def get_categories():
    categories = repos.auction_repo.get_categories()
    return {"categories": [category.to_public() for category in categories]}
