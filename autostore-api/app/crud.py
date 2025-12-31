from sqlalchemy.orm import Session
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate

# Create a new product
def create_product(db: Session, product: ProductCreate, seller_user_id: int, seller_username: str):
    db_product = Product(
        **product.dict(),  # Use the Pydantic model to fill product fields
        seller_user_id=seller_user_id,
        seller_username=seller_username
    )
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

# Get all products
def get_products(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Product).offset(skip).limit(limit).all()

# Get a product by ID
def get_product_by_id(db: Session, product_id: int):
    return db.query(Product).filter(Product.id == product_id).first()

# Update a product
def update_product(db: Session, product_id: int, product: ProductUpdate):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        for key, value in product.dict(exclude_unset=True).items():
            setattr(db_product, key, value)
        db.commit()
        db.refresh(db_product)
    return db_product

# Delete a product
def delete_product(db: Session, product_id: int):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product:
        db.delete(db_product)
        db.commit()
    return db_product
