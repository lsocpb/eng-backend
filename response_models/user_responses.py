from typing import Optional

from pydantic import BaseModel, EmailStr


class AddressResponse(BaseModel):
    street: str
    city: str
    zip: str


class ProfileResponse(BaseModel):
    username: str
    email: str
    profile_image_url: Optional[str]
    address: AddressResponse
    role: str


class EmailSchema(BaseModel):
    name: str
    email: EmailStr
    message: str
    to: EmailStr
