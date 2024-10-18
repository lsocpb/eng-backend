import os
from typing import Annotated

from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sendgrid import Mail, SendGridAPIClient
from sqlalchemy.orm import Session
from starlette.requests import Request

import db_management.dto
import repos.user_repo
import services.file_upload_service
import services.payment_gateway_service
from db_management.database import get_db
from response_models.auth_responses import validate_jwt
from response_models.user_responses import EmailSchema

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_jwt)]

load_dotenv()
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")
SENDGRID_FROM_EMAIL = os.getenv("SENDGRID_FROM_EMAIL")
SENDGRID_TO_EMAIL = os.getenv("SENDGRID_TO_EMAIL")


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user_info(db_user: user_dependency, db: db_dependency):
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user = repos.user_repo.get_by_id(db, db_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user.to_private()


@router.post("/upload_profile_image", status_code=status.HTTP_200_OK)
async def upload_profile_image(auth_user: user_dependency, db: db_dependency, file: UploadFile = File(...)):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    image_url = services.file_upload_service.upload_images([file])
    repos.user_repo.update_user_profile_image(db, user, image_url[0])
    return {"message": "Profile image uploaded successfully"}


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


@router.post("/wallet/topup", status_code=status.HTTP_200_OK)
async def create_payment(dto: db_management.dto.PaymentCreate, user: user_dependency, db: db_dependency):
    return {"payment_url": services.payment_gateway_service.create_payment_url(db, dto.amount, user['id'])}


@router.post("/wallet/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(db: db_dependency, request: Request):
    body = await request.body()
    body_str = body.decode("utf-8")

    services.payment_gateway_service.stripe_payment_webhook(db, body_str)
