import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, HTTPException, Header
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from starlette import status

from db_management.models import User, UserRole
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="auth/token")
internal_auth_token = OAuth2PasswordBearer(tokenUrl="auth/internal/token")


class AddressRequestCreate(BaseModel):
    street: str
    city: str
    zip: str


class CreateUserRequest(BaseModel):
    username: str
    password: str
    email: str
    phone: str
    address: AddressRequestCreate
    role: UserRole = Field(default=UserRole.USER)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

class Token(BaseModel):
    access_token: str
    token_type: str


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return pwd_context.verify(password, hashed_password)


def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    return user


def create_access_token(username: str, user_id: int, role: UserRole, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role.value}
    expires = datetime.utcnow() + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def validate_jwt(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get('sub')
        user_id = payload.get('id')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate credentials')
        return {'username': username, 'id': user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user')


async def validate_internal_auth(Authorization: str = Header()):
    if Authorization != internal_auth_token:
        raise HTTPException(status_code=400, detail="Unauthorized")


def get_current_user(token: str = Depends(oauth2_bearer)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")
        user_role: str = payload.get("role")
        if username is None or user_id is None or user_role is None:
            raise credentials_exception
        return {"username": username, "id": user_id, "role": UserRole(user_role)}
    except JWTError:
        raise credentials_exception


def admin_required(current_user: dict = Depends(get_current_user)):
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    return current_user

def validate_username(username: str):
    if len(username) < 3:
        return False
    if len(username) > 20:
        return False
    return True


def validate_password(password: str):
    if len(password) < 8:
        return False
    if len(password) > 40:
        return False
    return True


def validate_email(email: str):
    if len(email) < 5:
        return False
    if len(email) > 50:
        return False
    #todo regex
    return True