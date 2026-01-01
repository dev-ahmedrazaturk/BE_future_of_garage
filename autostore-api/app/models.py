# app/models.py
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Product Model

# Product Model
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    seller_user_id = Column(Integer, nullable=False)  # Ensure that seller_user_id is never null
    name = Column(String, index=True)
    description = Column(String)
    price = Column(Float)
    condition = Column(String)  # NEW/USED
    brand = Column(String)
    stock = Column(Integer)
    active = Column(Boolean, default=True)
    added_at = Column(DateTime, default=func.now())
    seller_username = Column(String)  # Store seller's username (optional)

    # Relationship with CartItem (if needed)
    cart_items = relationship("CartItem", back_populates="product")
    order_items = relationship("OrderItem", back_populates="product")  # Relationship to OrderItem
    reviews = relationship("Review", back_populates="product")  # Relationship to Review

# Cart Model
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    status = Column(String, default="ACTIVE")  # ACTIVE / CHECKED_OUT
    created_at = Column(DateTime, default=func.now())

    # Relationships
    items = relationship("CartItem", back_populates="cart")

# CartItem Model
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)

    # Relationships
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product", back_populates="cart_items")  # Added back_populates to Product

# Order Model
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    seller_user_id = Column(Integer)
    subtotal = Column(Float)
    tax = Column(Float)
    shipping_cost = Column(Float)
    discount_amount = Column(Float)
    total = Column(Float)
    status = Column(String, default="CREATED")  # CREATED / PAID / SHIPPED / DELIVERED / CANCELLED
    created_at = Column(DateTime, default=func.now())

    # Relationships
    items = relationship("OrderItem", back_populates="order")
    payment = relationship("Payment", back_populates="order", uselist=False)  # One payment per order
    shipment = relationship("Shipment", back_populates="order", uselist=False)  # One shipment per order

# OrderItem Model
class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    unit_price = Column(Float)

    # Relationships
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")  # Added back_populates to Product

# Payment Model
class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    transaction_id = Column(String)
    amount = Column(Float)
    status = Column(String, default="PENDING")  # SUCCESS / FAILED / PENDING
    created_at = Column(DateTime, default=func.now())

    # Relationships
    order = relationship("Order", back_populates="payment")

# Shipment Model
class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    carrier = Column(String)
    tracking_number = Column(String)
    status = Column(String, default="CREATED")  # CREATED / IN_TRANSIT / DELIVERED
    updated_at = Column(DateTime, default=func.now())

    # Relationships
    order = relationship("Order", back_populates="shipment")

# DiscountCode Model
class DiscountCode(Base):
    __tablename__ = "discount_codes"

    code = Column(String, primary_key=True)
    type = Column(String)  # PERCENT / FIXED
    value = Column(Float)
    valid_from = Column(DateTime)
    valid_to = Column(DateTime)
    active = Column(Boolean, default=True)

# Review Model
class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    user_id = Column(Integer)
    rating = Column(Integer)
    comment = Column(String)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    product = relationship("Product", back_populates="reviews")  # Added back_populates to Product
