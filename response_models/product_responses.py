from datetime import date

from pydantic import BaseModel


class ProductAddResponse(BaseModel):
    name: str
    description: str
    price: float
    status: str
    category_id: int
    image_url_1: str
    image_url_2: str
    image_url_3: str
    quantity: int
    end_date: date
    seller_id: int
    buyer_id: int
    created_at: str
    updated_at: str

class ProductGetResponse(BaseModel):
    name: str
    description: str
    price: float
    status: str
    category_id: int
    image_url_1: str
    image_url_2: str
    image_url_3: str
    quantity: int
    end_date: date
    seller_id: int
    buyer_id: int
    created_at: str
    updated_at: str