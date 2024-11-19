from datetime import timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from starlette import status

import response_models.auth_responses as auth
from db_management.dto import PersonalRegisterForm, CompanyRegisterForm
from response_models.auth_responses import Token, authenticate_user, \
    create_access_token
from services.user_service import create_personal_account, create_company_account
from utils.utils import old_get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

db_dependency = Annotated[Session, Depends(old_get_db)]


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
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate credentials')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=6000), user.account_type)

    return {'access_token': token, 'token_type': 'bearer'}


@router.get("/verify-token/{token}")
async def validate_token(token: str):
    await auth.validate_jwt(token=token)
    return {"message": "Token is valid"}
