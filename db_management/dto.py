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


class AddressRequestCreate(BaseModel):
    street: str = Field(max_length=255)
    city: str = Field(max_length=255)
    zip: str = Field(max_length=255)


class CreateUserRequest(BaseModel):
    username: str = Field(max_length=20)
    password: str = Field(max_length=32)
    email: str = Field(max_length=255)
    phone: str = Field(max_length=20)
    address: AddressRequestCreate = Field(description="Address details")
