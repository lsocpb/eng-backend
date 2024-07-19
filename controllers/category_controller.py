from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from db_management.models import Category
from response_models.category_responses import CategoryAddResponse
from typing import Annotated, Dict, Any

from utils.utils import get_db
from response_models.auth_responses import validate_jwt

router = APIRouter(
    prefix="/category",
    tags=["category"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Depends(validate_jwt)


# TODO Add a decorator to protect the endpoint with ADMIN JWT token
@router.post("/add", status_code=status.HTTP_201_CREATED)
async def add_category(db: db_dependency, category: CategoryAddResponse):
    db_category = Category(name=category.name, description=category.description, status=category.status, icon=category.icon)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return {"message": "Category added successfully"}


@router.get("/fetch/all", status_code=status.HTTP_200_OK)
async def get_categories(db: db_dependency):
    categories = db.query(Category).all()
    return {"categories": categories}


@router.delete("/delete", status_code=status.HTTP_200_OK)
async def delete_category(db: db_dependency,
                          category_id: int = Query(..., description="The ID of the category to delete")):
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"message": "Category deleted successfully"}

@router.get("/{category_id}", status_code=status.HTTP_200_OK)
async def get_category(
    db: db_dependency,
    category_id: int
) -> Dict[str, Any]:
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return {"id": category.id, "name": category.name}