import os
from typing import Annotated

import cloudinary.uploader
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sendgrid import Mail, SendGridAPIClient
from sqlalchemy.orm import Session

from db_management.models import User
from repos.user_repo import update_user_profile_image
from response_models.auth_responses import validate_jwt
from response_models.user_responses import ProfileResponse, AddressResponse, EmailSchema
from utils.utils import get_db, validate_image

router = APIRouter(
    tags=["user"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL")


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
                           address=address, role=details.role.value)


@router.post("/upload_profile_image", status_code=status.HTTP_200_OK)
async def upload_profile_image(user: user_dependency, db: db_dependency, file: UploadFile = File(...)):
    try:
        validate_image(file)

        result = cloudinary.uploader.upload(file.file)
        image_url = result.get('url')

        user_id = user['id']
        update_user_profile_image(user_id, image_url)

        return {"message": "Image uploaded successfully", "url": image_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/send-email", status_code=status.HTTP_200_OK)
async def send_email(email_data: EmailSchema):
    try:
        message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=SENDGRID_TO_EMAIL,
            subject=f"New message from {email_data.name}",
            html_content=f"""
                    <strong>Name:</strong> {email_data.name}<br>
                    <strong>Email:</strong> {email_data.email}<br>
                    <br>
                    <strong>Message:</strong><br>
                    {email_data.message}
                    """
        )

        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        return {"message": "Email sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
