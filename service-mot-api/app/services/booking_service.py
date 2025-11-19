# app/services/booking_service.py

from sqlalchemy.orm import Session
from .. import crud, schemas

class BookingService:
    def __init__(self, db: Session):
        self.db = db

    def create_booking(self, booking: schemas.BookingCreate):
        return crud.create_booking(self.db, booking)

    def get_bookings(self, skip: int = 0, limit: int = 10):
        return crud.get_bookings(self.db, skip, limit)

    def get_booking_by_registration(self, registration_number: str):
        return crud.get_booking_by_registration_number(self.db, registration_number)

    def update_booking(self, registration_number: str, updated_booking: schemas.BookingUpdate):
        return crud.update_booking(self.db, registration_number, updated_booking)

    def delete_booking(self, registration_number: str):
        return crud.delete_booking(self.db, registration_number)

class QuoteService:
    def __init__(self, db: Session):
        self.db = db

    def create_quote(self, quote: schemas.QuoteCreate, booking_id: int):
        return crud.create_quote(self.db, quote, booking_id)

    def get_quote_by_booking_id(self, booking_id: int):
        return crud.get_quote_by_booking_id(self.db, booking_id)

    def update_quote(self, booking_id: int, updated_quote: schemas.QuoteUpdate):
        return crud.update_quote(self.db, booking_id, updated_quote)

    def delete_quote(self, booking_id: int):
        return crud.delete_quote(self.db, booking_id)
