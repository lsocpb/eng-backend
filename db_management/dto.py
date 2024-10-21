from datetime import datetime

from pydantic import BaseModel, field_validator
from pydantic import Field
from pydantic import conlist

from utils.constants import AuctionType


# AUCTION

class CreateCategory(BaseModel):
    name: str = Field(max_length=255, description="Name of category")
    description: str = Field(default='', max_length=255, description="Description of category")
    icon: str = Field(default='', max_length=255, description="Icon of category")


class GetCategory(BaseModel):
    category_id: int = Field(description="ID of category")


class DeleteCategory(BaseModel):
    category_id: int = Field(description="ID of category")


class CreateAuctionProduct(BaseModel):
    name: str = Field(max_length=255, description="Name of product")
    description: str = Field(default='', max_length=255, description="Description of product")
    category_id: int = Field(description="Category ID of product")
    images: conlist(str, min_length=1, max_length=3) = Field(description="List of image files")

    # validate if image URL is from Cloudinary
    @field_validator("images")
    def validate_images(cls, value):
        for image in value:
            if not image.startswith("http://res.cloudinary.com"):
                raise ValueError("Image URL must be from Cloudinary")

        return value


class CreateAuction(BaseModel):
    auction_type: AuctionType = Field(default=AuctionType.BUY_NOW, description="Type of auction")
    end_date: datetime = Field(description="End date of auction")
    price: float = Field(ge=0.1, description="Price of product")
    product: CreateAuctionProduct = Field(description="Product details")

    # validate if end_date is not in the past
    @field_validator("end_date")
    def validate_end_date(cls, value: datetime):
        if int(value.timestamp()) < int(datetime.now().timestamp()):
            raise ValueError("End date cannot be in the past")

        return value


class GetAuction(BaseModel):
    auction_id: int = Field(description="ID of auction")


class SearchAuctions(BaseModel):
    keyword: str = Field(description="Search term")


class DeleteAuction(BaseModel):
    auction_id: int = Field(description="ID of auction")


class PlaceBid(BaseModel):
    auction_id: int = Field(description="ID of auction")
    bid_value: float = Field(ge=0.1, description="Bid value")


class BuyNow(BaseModel):
    auction_id: int = Field(description="ID of auction")


class PaymentCreate(BaseModel):
    amount: float = Field(ge=0.1, description="Amount to pay")


class AccountDetails(BaseModel):
    username: str = Field(max_length=20)
    password: str = Field(max_length=32)
    email: str = Field(max_length=255)

    @field_validator("email")
    def validate_email(cls, value):
        if "@" not in value:
            raise ValueError("Invalid email address")
        return value

    @field_validator("password")
    def validate_password(cls, value):
        if len(value) < 8 or len(value) > 20:
            raise ValueError("Password must be between 8 and 20 characters")
        return value

    @field_validator("username")
    def validate_username(cls, value):
        if len(value) < 3 or len(value) > 20:
            raise ValueError("Username must be between 3 and 20 characters")
        return value


class PersonalBilling(BaseModel):
    first_name: str = Field(max_length=255)
    last_name: str = Field(max_length=255)
    address: str = Field(max_length=255)
    postal_code: str = Field(max_length=255)
    city: str = Field(max_length=255)
    country: str = Field(max_length=255)
    phone_number: str = Field(max_length=255)


class CompanyBilling(BaseModel):
    company_name: str = Field(max_length=255)
    tax_id: str = Field(max_length=255)
    address: str = Field(max_length=255)
    postal_code: str = Field(max_length=255)
    city: str = Field(max_length=255)
    country: str = Field(max_length=255)
    phone_number: str = Field(max_length=255)
    bank_account: str = Field(max_length=255)


class PersonalRegisterForm(BaseModel):
    account_details: AccountDetails
    billing_details: PersonalBilling


class CompanyRegisterForm(BaseModel):
    account_details: AccountDetails
    billing_details: CompanyBilling
