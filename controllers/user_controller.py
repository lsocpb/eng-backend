from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session

from response_models.auth_responses import validate_jwt
from db_management.models import User
from response_models.user_responses import ProfileResponse, AddressResponse, ImageUploadResponse
from utils.utils import get_db

import cloudinary.uploader
from cloudinary.utils import cloudinary_url

router = APIRouter(
    tags=["user"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]


@router.get("/profile", status_code=status.HTTP_200_OK)
async def get_user_info(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user_id = user['id']

    details = db.query(User).filter(User.id == user_id).first()

    address = AddressResponse(street=details.address.street, city=details.address.city, zip=details.address.zip)

    if details is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Details not found")

    return ProfileResponse(username=details.username, email=details.email, profile_image_url=details.profile_image_url,
                           address=address)


@router.post("/upload_profile_image", status_code=status.HTTP_200_OK)
async def upload_profile_image(user: user_dependency, db: db_dependency, file: UploadFile = File(...)):
    try:
        result = cloudinary.uploader.upload(file.file)
        image_url = result.get('url')

        user_id = user['id']
        db_user = db.query(User).filter(User.id == user_id).first()

        db_user.profile_image_url = image_url
        db.commit()

        return {"message": "Image uploaded successfully", "url": image_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
