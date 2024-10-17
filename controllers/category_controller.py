from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

import repos.auction_repo
import repos.user_repo
from db_management import dto
from db_management.database import get_db
from response_models.auth_responses import validate_jwt

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Depends(validate_jwt)


@router.get("/{category_id}", status_code=status.HTTP_200_OK)
async def get_category(category_id: str, db: db_dependency):
    # Get all categories
    if category_id == "all":
        categories = repos.auction_repo.get_categories(db)
        return {"categories": [category.to_public() for category in categories]}
    # Get a specific category
    elif category_id.isnumeric():
        category = repos.auction_repo.get_category_by_id(db, int(category_id))
        if category is None:
            raise HTTPException(status_code=404, detail="Category not found")

        return category.to_public()
    else:
        raise HTTPException(status_code=400, detail="Invalid category id")


@router.put("", status_code=status.HTTP_201_CREATED)
async def create_category(category: dto.CreateCategory, db: db_dependency):
    repos.auction_repo.create_category(db, category)
    return {"message": "Category added successfully"}


@router.delete("", status_code=status.HTTP_200_OK)
async def delete_category(dto: dto.DeleteCategory, db: db_dependency):
    repos.auction_repo.delete_category(db, dto.category_id)
    return {"message": "Category deleted successfully"}
