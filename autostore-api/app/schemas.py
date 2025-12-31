from pydantic import BaseModel
from typing import Optional

class ProductBase(BaseModel):
    name: str
    description: str
    price: float
    condition: str  # NEW/USED
    brand: str
    stock: int
    active: bool = True  # Default to True

class ProductCreate(ProductBase):
    pass  # Product creation requires all fields from ProductBase

class ProductUpdate(ProductBase):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    condition: Optional[str] = None
    brand: Optional[str] = None
    stock: Optional[int] = None
    active: Optional[bool] = None

class Product(ProductBase):
    id: int
    seller_user_id: int
    seller_username: Optional[str] = None
    added_at: str

    class Config:
        orm_mode = True  # This is necessary for SQLAlchemy ORM models to Pydantic conversion
