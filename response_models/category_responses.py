from pydantic import BaseModel


class CategoryAddResponse(BaseModel):
    name: str
    description: str
    status: str