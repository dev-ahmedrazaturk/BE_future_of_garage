# app/crud.py
from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductCreate


def create_product(db: Session, product: ProductCreate):
    # Extract seller_user_id explicitly
    seller_user_id = product.seller_user_id
    
    # Create a Product object without passing seller_user_id again through product.dict()
    db_product = Product(
        **product.dict(exclude={"seller_user_id"}),  # Use product.dict() excluding seller_user_id
        seller_user_id=seller_user_id  # Explicitly set seller_user_id here
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_product(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Product).offset(skip).limit(limit).all()

def update_product(db: Session, product_id: int, product: ProductCreate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
