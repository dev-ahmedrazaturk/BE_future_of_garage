from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional


# ==================== Base Schema ====================

class BaseSchema(BaseModel):
    added_at: Optional[datetime] = None

    class Config:
        orm_mode = True

    @validator("added_at", pre=True, always=True)
    def format_added_at(cls, v):
        if isinstance(v, datetime):
            return v.isoformat()  # Converts datetime to ISO format string
        return v


# ==================== Product Schemas ====================

class ProductBase(BaseSchema):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    condition: Optional[str] = None  # NEW/USED
    brand: Optional[str] = None
    stock: Optional[int] = None
    active: Optional[bool] = None
    seller_user_id: Optional[int] = None  # Optional field for seller's user ID
    seller_username: Optional[str] = None  # Optional field for seller's username


class ProductCreate(ProductBase):
    name: str
    description: str
    price: float
    condition: str
    brand: str
    stock: int


class ProductUpdate(ProductBase):
    pass  # All fields are optional and handled by ProductBase


class ProductResponse(ProductBase):
    id: int
    seller_user_id: int
    added_at: str  # formatted as a string

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        if isinstance(obj.added_at, datetime):
            obj.added_at = obj.added_at.strftime('%Y-%m-%d %H:%M:%S')  # Custom format
        return obj


# ==================== Cart Schemas ====================

class CartBase(BaseSchema):
    user_id: Optional[int] = None
    status: Optional[str] = "ACTIVE"  # ACTIVE / CHECKED_OUT


class CartCreate(CartBase):
    user_id: int


class CartUpdate(CartBase):
    pass


class CartResponse(CartBase):
    id: int
    created_at: str

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        if isinstance(obj.created_at, datetime):
            obj.created_at = obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return obj


# ==================== CartItem Schemas ====================

class CartItemBase(BaseSchema):
    cart_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


class CartItemCreate(CartItemBase):
    cart_id: int
    product_id: int
    quantity: int
    unit_price: float


class CartItemUpdate(CartItemBase):
    pass


class CartItemResponse(CartItemBase):
    id: int

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj


# ==================== Order Schemas ====================

class OrderBase(BaseSchema):
    user_id: Optional[int] = None
    seller_user_id: Optional[int] = None
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    shipping_cost: Optional[float] = None
    discount_amount: Optional[float] = None
    total: Optional[float] = None
    status: Optional[str] = "CREATED"  # CREATED / PAID / SHIPPED / DELIVERED / CANCELLED


class OrderCreate(OrderBase):
    user_id: int
    seller_user_id: int
    subtotal: float
    tax: float
    shipping_cost: float
    discount_amount: float
    total: float
    status: str


class OrderUpdate(OrderBase):
    pass


class OrderResponse(OrderBase):
    id: int
    created_at: str

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        if isinstance(obj.created_at, datetime):
            obj.created_at = obj.created_at.strftime('%Y-%m-%d %H:%M:%S')
        return obj


# ==================== OrderItem Schemas ====================

class OrderItemBase(BaseSchema):
    order_id: Optional[int] = None
    product_id: Optional[int] = None
    quantity: Optional[int] = None
    unit_price: Optional[float] = None


class OrderItemCreate(OrderItemBase):
    order_id: int
    product_id: int
    quantity: int
    unit_price: float


class OrderItemUpdate(OrderItemBase):
    pass


class OrderItemResponse(OrderItemBase):
    id: int

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj


# ==================== Payment Schemas ====================

class PaymentBase(BaseSchema):
    order_id: Optional[int] = None
    transaction_id: Optional[str] = None
    amount: Optional[float] = None
    status: Optional[str] = "PENDING"  # SUCCESS / FAILED / PENDING


class PaymentCreate(PaymentBase):
    order_id: int
    transaction_id: str
    amount: float
    status: str


class PaymentUpdate(PaymentBase):
    pass


class PaymentResponse(PaymentBase):
    id: int

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj


# ==================== Shipment Schemas ====================

class ShipmentBase(BaseSchema):
    order_id: Optional[int] = None
    carrier: Optional[str] = None
    tracking_number: Optional[str] = None
    status: Optional[str] = "CREATED"  # CREATED / IN_TRANSIT / DELIVERED


class ShipmentCreate(ShipmentBase):
    order_id: int
    carrier: str
    tracking_number: str
    status: str


class ShipmentUpdate(ShipmentBase):
    pass


class ShipmentResponse(ShipmentBase):
    id: int

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj


# ==================== DiscountCode Schemas ====================

class DiscountCodeBase(BaseSchema):
    code: Optional[str] = None
    type: Optional[str] = None  # PERCENT / FIXED
    value: Optional[float] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    active: Optional[bool] = True


class DiscountCodeCreate(DiscountCodeBase):
    code: str
    type: str
    value: float
    valid_from: datetime
    valid_to: datetime


class DiscountCodeUpdate(DiscountCodeBase):
    pass


class DiscountCodeResponse(DiscountCodeBase):
    code: str

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj


# ==================== Review Schemas ====================

class ReviewBase(BaseSchema):
    product_id: Optional[int] = None
    user_id: Optional[int] = None
    rating: Optional[int] = None
    comment: Optional[str] = None


class ReviewCreate(ReviewBase):
    product_id: int
    user_id: int
    rating: int
    comment: str


class ReviewUpdate(ReviewBase):
    pass


class ReviewResponse(ReviewBase):
    id: int

    @classmethod
    def from_orm(cls, obj):
        obj = super().from_orm(obj)
        return obj
