from sqlalchemy.orm import Session
from . import models, schemas

# Booking CRUD
def create_booking(db: Session, booking: schemas.BookingCreate):
    db_booking = models.Booking(**booking.dict())
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def get_bookings_by_status(db: Session, skip: int = 0, limit: int = 10, status: str = "Pending"):
    return db.query(models.Booking).filter(models.Booking.status == status).offset(skip).limit(limit).all()

def get_booking_by_registration_number(db: Session, registration_number: str):
    return db.query(models.Booking).filter(models.Booking.vehicle_reg_number == registration_number).first()

def update_booking(db: Session, registration_number: str, updated_booking: schemas.BookingUpdate):
    db_booking = db.query(models.Booking).filter(models.Booking.vehicle_reg_number == registration_number).first()
    if db_booking:
        for key, value in updated_booking.dict(exclude_unset=True).items():
            setattr(db_booking, key, value)
        db.commit()
        db.refresh(db_booking)
        return db_booking
    return None

def delete_booking(db: Session, registration_number: str):
    db_booking = db.query(models.Booking).filter(models.Booking.vehicle_reg_number == registration_number).first()
    if db_booking:
        db.delete(db_booking)
        db.commit()
        return {"msg": "Booking deleted"}
    return {"msg": "Booking not found"}

def update_booking_status(db: Session, booking_id: int, status: str):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        return None

    booking.status = status
    db.commit()
    db.refresh(booking)
    return booking


# Quote CRUD
def create_quote(db: Session, quote: schemas.QuoteCreate, booking_id: int):
    db_quote = models.Quote(**quote.dict(), booking_id=booking_id)
    db.add(db_quote)
    db.commit()
    db.refresh(db_quote)
    return db_quote

def get_quote_by_booking_id(db: Session, booking_id: int):
    return db.query(models.Quote).filter(models.Quote.booking_id == booking_id).first()

def update_quote(db: Session, booking_id: int, updated_quote: schemas.QuoteUpdate):
    db_quote = db.query(models.Quote).filter(models.Quote.booking_id == booking_id).first()
    if db_quote:
        for key, value in updated_quote.dict(exclude_unset=True).items():
            setattr(db_quote, key, value)
        db.commit()
        db.refresh(db_quote)
        return db_quote
    return None

def delete_quote(db: Session, booking_id: int):
    db_quote = db.query(models.Quote).filter(models.Quote.booking_id == booking_id).first()
    if db_quote:
        db.delete(db_quote)
        db.commit()
        return {"msg": "Quote deleted"}
    return {"msg": "Quote not found"}
