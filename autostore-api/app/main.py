import os
import sys
import stripe

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordBearer, HTTPBearer
from sqlalchemy.orm import Session
from typing import List
from app.database import SessionLocal, engine, Base
from app import crud, models, schemas
from app.schemas import CartCreate, CartUpdate, CartResponse, PaymentCreate, PaymentResponse
from app.crud import create_payment

# Ensure we can import the shared package from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.jwt_utils import decode_access_token 

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



# Cart Endpoints


@app.post("/carts/", response_model=CartResponse)
def create_cart(cart: CartCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("sub")  # Get the user ID from JWT token

    # Create Cart object
    db_cart = models.Cart(
        user_id=user_id,  # Set the user_id dynamically from the token
        status=cart.status  # Use the status from the incoming request
    )

    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)

    return db_cart 

# Get a cart by its ID
@app.get("/carts/{cart_id}", response_model=CartResponse)
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    db_cart = crud.get_cart(db=db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return db_cart

# Get all carts with pagination
@app.get("/carts/", response_model=List[CartResponse])
def get_carts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    carts = crud.get_carts(db=db, skip=skip, limit=limit)
    return carts

# Update a cart by its ID
@app.put("/carts/{cart_id}", response_model=CartResponse)
def update_cart(cart_id: int, cart: CartUpdate, db: Session = Depends(get_db)):
    db_cart = crud.update_cart(db=db, cart_id=cart_id, cart=cart)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return db_cart

# Delete a cart by its ID
@app.delete("/carts/{cart_id}", response_model=CartResponse)
def delete_cart(cart_id: int, db: Session = Depends(get_db)):
    db_cart = crud.delete_cart(db=db, cart_id=cart_id)
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return db_cart

@app.get("/carts/active/{user_id}", response_model=schemas.CartResponse)
def get_active_cart_by_user(user_id: int, db: Session = Depends(get_db)):
    # Call the CRUD function to get the active cart for the user
    db_cart = crud.get_active_cart_by_user(db, user_id)
    
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Active cart not found for this user")
    
    return db_cart


@app.post("/cart-items/", response_model=schemas.CartItemResponse)
def add_cart_item(cart_item: schemas.CartItemCreate, db: Session = Depends(get_db)):
    # Ensure that the cart exists, you may want to check if cart_id is valid
    db_cart_item = crud.create_cart_item(db=db, cart_item=cart_item)
    return db_cart_item

@app.delete("/cart-items/{cart_item_id}", response_model=schemas.CartItemResponse)
def remove_cart_item(cart_item_id: int, db: Session = Depends(get_db)):
    # Ensure that the cart item exists before trying to delete
    db_cart_item = crud.delete_cart_item(db=db, cart_item_id=cart_item_id)
    if db_cart_item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return db_cart_item


@app.get("/carts/{cart_id}/items", response_model=List[schemas.CartItemResponse])
def get_cart_items(cart_id: int, db: Session = Depends(get_db)):
    # Retrieve the cart items for the given cart_id
    cart_items = crud.get_cart_items_by_cart_id(db=db, cart_id=cart_id)
    if not cart_items:
        raise HTTPException(status_code=404, detail="No items found in this cart")
    return cart_items


# Order endpoints 
@app.post("/orders/", response_model=schemas.OrderResponse)
def create_order(order: schemas.OrderCreate, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    try:
        # Create an order based on the current user and provided order details
        db_order = models.Order(
            user_id=current_user.get("sub"),  # Get current user id from JWT token
            seller_user_id=order.seller_user_id,
            subtotal=order.subtotal,
            tax=order.tax,
            shipping_cost=order.shipping_cost,
            discount_amount=order.discount_amount,
            total=order.total,
            status=order.status,
        )

        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        
        # Create order items for the order
        for item in order.items:
            db_order_item = models.OrderItem(
                order_id=db_order.id,
                product_id=item.product_id,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            db.add(db_order_item)
        db.commit()

        return db_order
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Validation Error: {str(e)}")


@app.get("/orders/{order_id}", response_model=schemas.OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.get_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order



@app.get("/orders/", response_model=List[schemas.OrderResponse])
def get_orders(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    orders = crud.get_orders(db, skip, limit, user_id=current_user.get("sub"))
    return orders

@app.put("/orders/{order_id}", response_model=schemas.OrderResponse)
def update_order_status(order_id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)):
    db_order = crud.update_order_status(db, order_id, order)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.delete("/orders/{order_id}", response_model=schemas.OrderResponse)
def delete_order(order_id: int, db: Session = Depends(get_db)):
    db_order = crud.delete_order(db, order_id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order

@app.post("/order-items/", response_model=schemas.OrderItemResponse)
def create_order_item(order_item: schemas.OrderItemCreate, db: Session = Depends(get_db)):
    db_order_item = models.OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        unit_price=order_item.unit_price
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

@app.get("/order-items/{order_item_id}", response_model=schemas.OrderItemResponse)
def get_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_order_item = crud.get_order_item(db, order_item_id)
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return db_order_item

@app.delete("/order-items/{order_item_id}", response_model=schemas.OrderItemResponse)
def delete_order_item(order_item_id: int, db: Session = Depends(get_db)):
    db_order_item = crud.delete_order_item(db, order_item_id)
    if db_order_item is None:
        raise HTTPException(status_code=404, detail="Order Item not found")
    return db_order_item


@app.get("/order-items/order/{order_id}", response_model=List[schemas.OrderItemResponse])
def get_order_items_by_order(order_id: int, db: Session = Depends(get_db)):
    db_order_items = crud.get_order_items_by_order(db, order_id)
    if db_order_items is None:
        raise HTTPException(status_code=404, detail="Order items not found")
    return db_order_items


#payments
stripe.api_key = "sk_test_51skogIDTy09Pqg1f11B8RpnNyMkMmDTq5TL3ukooQxCukt1QZcCj6e6Keye21EjayblwcdQ3orSyk4mNcbza1tZhg920aEsNg7XS"
@app.post("/payments/", response_model=PaymentResponse)
def create_payment_endpoint(payment: PaymentCreate, db: Session = Depends(get_db)):
    return create_payment(db=db, payment=payment)





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
