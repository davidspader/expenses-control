from  pydantic import field_validator
from app.schemas.base import CustomBaseModel

class Category(CustomBaseModel):
    name: str

    @field_validator('name')
    def validate_name(cls, value):
        if len(value) == 0:
            raise ValueError("empty name not allowed")
        return value
class CategoryOutput(Category):
    id: int
    user_id: int

    class Config:
        orm_mode=True