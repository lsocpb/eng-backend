import json
import os
from typing import Annotated

import stripe
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sendgrid import Mail, SendGridAPIClient
from sqlalchemy.orm import Session
from starlette.requests import Request

import db_management.dto
import repos.user_repo
import services.file_upload_service
from db_management.database import get_db
from db_management.models import User
from response_models.auth_responses import validate_jwt
from response_models.user_responses import ProfileResponse, AddressResponse, EmailSchema

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
    try:
        YOUR_DOMAIN = "https://charfair.me"
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price_data': {
                        'currency': 'pln',
                        'product_data': {
                            'name': 'Doładowanie portfela CharFair',
                        },
                        'unit_amount': int(dto.amount * 100)
                    },
                    'quantity': 1
                }
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success.html',
            cancel_url=YOUR_DOMAIN + '/cancel.html',
            automatic_tax={'enabled': False},
            metadata={'user_id': user['id']}
        )
    except Exception as e:
        return str(e)

    return {"payment_url": checkout_session.url}


@router.post("/wallet/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request):
    body = await request.body()
    body_str = body.decode("utf-8")
    event = None

    try:
        event = stripe.Event.construct_from(
            json.loads(body_str), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        raise HTTPException(status_code=400, detail="Invalid payload")

    # Handle the event
    if event.type == 'checkout.session.completed':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        print(f"Payment checkout succeeded: {payment_intent}")
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event.type == 'payment_method.attached':
        payment_method = event.data.object  # contains a stripe.PaymentMethod
        print(f"Payment method attached: {payment_method}")
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    # ... handle other event types
    else:
        print('Unhandled event type {}'.format(event.type))
