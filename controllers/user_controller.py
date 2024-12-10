from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from starlette.requests import Request

import db_management.dto
import repos.user_repo
import services.file_upload_service
import services.stripe_service
from db_management.database import get_db
from response_models.auth_responses import validate_auth_jwt
from response_models.auth_responses import verify_password
from utils.constants import UserAccountType

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(validate_auth_jwt)]


@router.get("/me", status_code=status.HTTP_200_OK)
async def get_user_info(db_user: user_dependency, db: db_dependency):
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    user = repos.user_repo.get_by_id(db, db_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user.to_private()


@router.put("/change_password", status_code=status.HTTP_200_OK)
async def change_password(dto: db_management.dto.PasswordChange, db_user: user_dependency, db: db_dependency):
    user = repos.user_repo.get_by_id(db, db_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if not verify_password(dto.old_password, user.password_hash):
        raise HTTPException(status_code=400, detail="Old password is incorrect")

    repos.user_repo.change_user_password(db, user, dto.new_password)
    return {"message": "Password changed successfully"}


@router.post("/upload_profile_image", status_code=status.HTTP_200_OK)
async def upload_profile_image(auth_user: user_dependency, db: db_dependency, file: UploadFile = File(...)):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    image_url = services.file_upload_service.upload_images([file])
    repos.user_repo.update_user_profile_image(db, user, image_url[0])
    return {"message": "Profile image uploaded successfully"}


@router.get("/purchases", status_code=status.HTTP_200_OK)
async def get_user_purchases(auth_user: user_dependency, db: db_dependency):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.account_type != UserAccountType.PERSONAL:
        raise HTTPException(status_code=403, detail="Only personal accounts can view purchases history")

    return {"purchases": [purchase.to_public() for purchase in user.products_bought]}


@router.get("/sales", status_code=status.HTTP_200_OK)
async def get_user_sales(auth_user: user_dependency, db: db_dependency):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if user.account_type != UserAccountType.BUSINESS:
        raise HTTPException(status_code=403, detail="Only business accounts can view sales history")

    return {"sales": [sale.to_public() for sale in user.products_sold]}


@router.get("/wallet", status_code=status.HTTP_200_OK)
async def get_wallet_balance(auth_user: user_dependency, db: db_dependency):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"balance_total": user.balance_total, "balance_reserved": user.balance_reserved}


@router.post("/wallet/topup", status_code=status.HTTP_200_OK)
async def create_payment(dto: db_management.dto.PaymentCreate, user: user_dependency, db: db_dependency):
    return {"payment_url": services.stripe_service.create_payment_url(db, dto.amount, user['id'])}


@router.post("/wallet/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(db: db_dependency, request: Request):
    body = await request.body()
    body_str = body.decode("utf-8")

    services.stripe_service.stripe_payment_webhook(db, body_str)


@router.get("/wallet/transactions", status_code=status.HTTP_200_OK)
async def get_wallet_transactions(auth_user: user_dependency, db: db_dependency):
    user = repos.user_repo.get_by_id(db, auth_user['id'])
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return {"transactions": [transaction.to_public() for transaction in user.wallet_transactions]}
