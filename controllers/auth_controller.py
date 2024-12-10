from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import repos.user_repo
import response_models.auth_responses as auth
import services.email_service
from db_management.database import get_db
from db_management.dto import PersonalRegisterForm, CompanyRegisterForm, PasswordRecoveryByToken, PasswordRecoveryStart
from db_management.models import User
from response_models.auth_responses import Token, authenticate_user, \
    create_access_token
from services.user_service import create_personal_account, create_company_account

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

db_dependency = Annotated[Session, Depends(get_db)]


@router.post('/register/personal', status_code=status.HTTP_201_CREATED)
async def register_personal_account(db: db_dependency, dto: PersonalRegisterForm):
    create_personal_account(db, dto)
    return {'message': 'User registered successfully'}


@router.post('/register/company', status_code=status.HTTP_201_CREATED)
async def register_company_account(db: db_dependency, dto: CompanyRegisterForm):
    create_company_account(db, dto)
    return {'message': 'User registered successfully'}


@router.post('/token', response_model=Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
    user__all = db.query(User).all()
    for user in user__all:
        print(user.to_private())

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')
    token = create_access_token(user, timedelta(minutes=6000))

    return {'access_token': token, 'token_type': 'bearer'}


@router.post('/recover_password/token', status_code=status.HTTP_201_CREATED)
async def reset_password(db: db_dependency, dto: PasswordRecoveryByToken):
    user_id = auth.validate_reset_pwd_jwt(dto.token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')

    user = repos.user_repo.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail='User not found')

    repos.user_repo.change_user_password(db, user, dto.new_password)
    return {'message': 'Password changed successfully'}


@router.post('/recover_password', status_code=status.HTTP_201_CREATED)
async def recover_password(db: db_dependency, dto: PasswordRecoveryStart):
    user = repos.user_repo.get_by_email(db, dto.email)
    if not user:
        return {'message': 'If the user exists, a password reset link has been sent to the email address'}

    token = auth.create_reset_password_token(user.id)
    services.email_service.send_password_reset_email(user.email, f"https://charfair.me/login/reset-password/?token={token}")
    return {'message': 'If the user exists, a password reset link has been sent to the email address'}


@router.get("/verify-token/{token}")
async def validate_token(token: str):
    await auth.validate_auth_jwt(token=token)
    return {"message": "Token is valid"}
