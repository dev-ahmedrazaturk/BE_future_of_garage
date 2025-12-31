from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, engine, Base
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate, Product
from app.crud import create_product, get_products, get_product_by_id, update_product, delete_product
import jwt

# OAuth2PasswordBearer for extracting the token from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to extract user data from the JWT token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the JWT token and extract user info
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        user_id = payload.get("sub")  # Assuming the user ID is in the 'sub' field
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "username": payload.get("username")}
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Create FastAPI instance
app = FastAPI()

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Product Routes with Authorization
@app.post("/products/", response_model=Product)
def create_new_product(
    product: ProductCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)
):
    seller_user_id = current_user["user_id"]
    seller_username = current_user["username"]
    return create_product(db=db, product=product, seller_user_id=seller_user_id, seller_username=seller_username)

@app.get("/products/", response_model=List[Product])
def read_products(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return get_products(db=db, skip=skip, limit=limit)

@app.get("/products/{product_id}", response_model=Product)
def read_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product_by_id(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@app.put("/products/{product_id}", response_model=Product)
def update_existing_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    db_product = get_product_by_id(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return update_product(db=db, product_id=product_id, product=product)

@app.delete("/products/{product_id}", response_model=Product)
def delete_existing_product(product_id: int, db: Session = Depends(get_db)):
    db_product = get_product_by_id(db=db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return delete_product(db=db, product_id=product_id)

# Correctly Modify OpenAPI Schema
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

# Override the default OpenAPI generation to include our custom security
app.openapi_schema = app.openapi()  # Ensure this line is here before overriding
app.openapi = get_openapi
