# app/crud.py
from http.client import HTTPException
import logging
from sqlalchemy.orm import Session
import stripe
from app.models import Cart, CartItem, Order, OrderItem, Payment, Product
from app.schemas import CartItemCreate, OrderCreate, OrderItemCreate, OrderUpdate, PaymentCreate, ProductCreate, CartCreate, CartUpdate, CartResponse
from fastapi import HTTPException, status

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

# Create a new Cart
def create_cart(db: Session, cart: CartCreate):
    db_cart = Cart(user_id=cart.user_id, status=cart.status)
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

# Get a cart by its ID
def get_cart(db: Session, cart_id: int):
    return db.query(Cart).filter(Cart.id == cart_id).first()

# Get all carts with pagination
def get_carts(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Cart).offset(skip).limit(limit).all()

# Update a cart
def update_cart(db: Session, cart_id: int, cart: CartUpdate):
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if db_cart:
        for key, value in cart.dict(exclude_unset=True).items():
            setattr(db_cart, key, value)
        db.commit()
        db.refresh(db_cart)
    return db_cart

# Delete a cart
def delete_cart(db: Session, cart_id: int):
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if db_cart:
        db.delete(db_cart)
        db.commit()
    return db_cart


def get_active_cart_by_user(db: Session, user_id: int):
    # Query the Cart table to get the active cart by user_id
    return db.query(Cart).filter(Cart.user_id == user_id, Cart.status == "ACTIVE").first()



def create_cart_item(db: Session, cart_item: CartItemCreate):
    db_cart_item = CartItem(
        cart_id=cart_item.cart_id,
        product_id=cart_item.product_id,
        quantity=cart_item.quantity,
        unit_price=cart_item.unit_price
    )
    db.add(db_cart_item)
    db.commit()
    db.refresh(db_cart_item)
    return db_cart_item



def delete_cart_item(db: Session, cart_item_id: int):
    db_cart_item = db.query(CartItem).filter(CartItem.id == cart_item_id).first()
    if db_cart_item:
        db.delete(db_cart_item)
        db.commit()
    return db_cart_item


def get_cart_items_by_cart_id(db: Session, cart_id: int):
    return db.query(CartItem).filter(CartItem.cart_id == cart_id).all()




def get_order(db: Session, order_id: int):
    return db.query(Order).filter(Order.id == order_id).first()

def get_orders(db: Session, skip: int = 0, limit: int = 10, user_id: int = None):
    query = db.query(Order)
    if user_id:
        query = query.filter(Order.user_id == user_id)
    return query.offset(skip).limit(limit).all()

def create_order(db: Session, order: OrderCreate):
    db_order = Order(
        user_id=order.user_id,
        seller_user_id=order.seller_user_id,
        subtotal=order.subtotal,
        tax=order.tax,
        shipping_cost=order.shipping_cost,
        discount_amount=order.discount_amount,
        total=order.total,
        status=order.status
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order_status(db: Session, order_id: int, order: OrderUpdate):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        for key, value in order.dict(exclude_unset=True).items():
            setattr(db_order, key, value)
        db.commit()
        db.refresh(db_order)
    return db_order

def delete_order(db: Session, order_id: int):
    db_order = db.query(Order).filter(Order.id == order_id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
    return db_order

# OrderItem CRUD functions
def create_order_item(db: Session, order_item: OrderItemCreate):
    db_order_item = OrderItem(
        order_id=order_item.order_id,
        product_id=order_item.product_id,
        quantity=order_item.quantity,
        unit_price=order_item.unit_price
    )
    db.add(db_order_item)
    db.commit()
    db.refresh(db_order_item)
    return db_order_item

def get_order_item(db: Session, order_item_id: int):
    return db.query(OrderItem).filter(OrderItem.id == order_item_id).first()

def delete_order_item(db: Session, order_item_id: int):
    db_order_item = db.query(OrderItem).filter(OrderItem.id == order_item_id).first()
    if db_order_item:
        db.delete(db_order_item)
        db.commit()
    return db_order_item

def get_order_items_by_order(db: Session, order_id: int):
    return db.query(OrderItem).filter(OrderItem.order_id == order_id).all()



stripe.api_key = "sk_test_51SkogIDTy0PGqlf1EOTNAoaX6Pl2cXfcmO7bWzB66BcAlMekEArbVRKmCUs17KwiY6xT6LE0sz6UZ60CihN148Gf00nnIRBW9w"

def create_payment(db: Session, payment: PaymentCreate):
    try:
        # Log the details of the payment request
        logging.info(f"Creating payment with the following details: order_id={payment.order_id} transaction_id='{payment.transaction_id}' amount={payment.amount} status='{payment.status}'")
        
        # Create a PaymentIntent with Stripe and use automatic payment methods
        intent = stripe.PaymentIntent.create(
            amount=int(payment.amount * 100),
            currency='gbp',
            payment_method=payment.transaction_id,
            automatic_payment_methods={
                'enabled': True
            }
        )
        
        # After the payment is confirmed, create the payment entry in the DB
        db_payment = Payment(
            order_id=payment.order_id,
            transaction_id=intent.id,  # Using the PaymentIntent ID from Stripe
            amount=payment.amount,
            status=intent.status  # Using the Stripe payment status
        )
        
        db.add(db_payment)
        db.commit()
        db.refresh(db_payment)
        
        logging.info(f"Payment successfully created: {db_payment}")
        return db_payment  # Return the created payment record
    
    except stripe.error.CardError as e:
        # Catch card errors (invalid card, insufficient funds, etc.)
        body = e.json_body
        err = body.get('error', {})
        logging.error(f"Card Error: {err.get('message')}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment failed: {err.get('message')}"
        )
    
    except stripe.error.StripeError as e:
        # Catch general Stripe API errors
        logging.error(f"Stripe Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the payment."
        )
    
    except Exception as e:
        # Catch any other unforeseen errors
        logging.error(f"Unexpected Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

