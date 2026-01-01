import os
import sys
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, engine, Base
from app import crud, models, schemas

# Ensure we can import the shared package from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from shared.jwt_utils import decode_access_token  # noqa: E402

# OAuth2PasswordBearer for extracting the token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Instantiate the HTTPBearer to extract the token from the Authorization header
security = HTTPBearer()

# Dependency to get current user from the decoded token
def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    payload = decode_access_token(creds.credentials)  # Decode the token
    
    print("Decoded payload:", payload)  # Debugging line to check the decoded payload
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Return the decoded payload, which contains the user's info (sub, fullname, email, role)
    return payload

# Create FastAPI instance
app = FastAPI(title="Auto store API")

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Product Endpoints
@app.post("/products/", response_model=schemas.ProductResponse)
def create_new_product(product: schemas.ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    # Create a new Product model instance (SQLAlchemy model)
    db_product = models.Product(
        name=product.name,
        description=product.description,
        price=product.price,
        condition=product.condition,
        brand=product.brand,
        stock=product.stock,
        seller_user_id=current_user.get("sub"),  # Use 'sub' or whatever the field name is
        seller_username=current_user.get("fullname"),  # Use 'fullname' or whatever the field name is
    )

    # Add the product to the database
    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@app.get("/products/{product_id}", response_model=schemas.ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.get_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.get("/products/", response_model=List[schemas.ProductResponse])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    # Get the list of products
    products = crud.get_products(db=db, skip=skip, limit=limit)

    # Ensure that seller_user_id is not None
    for product in products:
        if product.seller_user_id is None:
            raise HTTPException(status_code=400, detail="Seller user ID is missing.")

    return products

@app.put("/products/{product_id}", response_model=schemas.ProductResponse)
def update_product(product_id: int, product: schemas.ProductUpdate, db: Session = Depends(get_db)):
    db_product = crud.update_product(db=db, product_id=product_id, product=product)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.delete("/products/{product_id}", response_model=schemas.ProductResponse)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    db_product = crud.delete_product(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

# Override the default OpenAPI generation to include our custom security
def get_openapi():
    # Generate OpenAPI schema using FastAPI's default implementation
    openapi_schema = app.openapi_schema  # Use the default OpenAPI schema from FastAPI
    
    # Add JWT Bearer authentication globally to the OpenAPI schema
    openapi_schema["components"]["securitySchemes"] = {
        "bearerAuth": {
            "type": "http",
            "scheme": "bearer",  # JWT Bearer token
            "bearerFormat": "JWT",  # JWT token format
        }
    }

    # Apply security globally for all routes in the OpenAPI schema
    openapi_schema["security"] = [{"bearerAuth": []}]
    
    return openapi_schema

# Override the default OpenAPI generation
app.openapi_schema = app.openapi()
app.openapi = get_openapi
