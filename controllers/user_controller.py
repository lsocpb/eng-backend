from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from response_models.auth_responses import validate_jwt
from db_management.models import User
from response_models.user_responses import ProfileResponse, AddressResponse
from utils.utils import get_db

router = APIRouter(
    tags=["user"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

@router.get("/profile" , status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    details = db.query(User).filter(User.id == user_id).first()

    address = AddressResponse(street=details.address.street, city=details.address.city, zip=details.address.zip)

    if details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Details not found")

    return ProfileResponse(username=details.username, email=details.email, address=address)