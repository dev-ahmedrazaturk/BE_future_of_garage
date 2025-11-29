from pydantic import BaseModel
from datetime import date, time
from enum import Enum

# Enum for booking status
class BookingStatus(str, Enum):
    Pending = "Pending"
    Approved = "Approved"
    Rejected = "Rejected"
    Completed = "Completed"

class BookingBase(BaseModel):
    name: str  # Client name
    vehicle: str  # General vehicle information
    vehicle_make: str  # Vehicle Make
    vehicle_model: str  # Vehicle Model
    vehicle_year: int  # Vehicle Year
    vehicle_reg_number: str  # Vehicle Registration Number
    engine_size: str  # Engine Size
    fuel_type: str  # Fuel Type
    transmission: str  # Transmission Type
    mileage: int  # Mileage
    additional_notes: str  # Additional Notes
    selected_garage: str  # Selected Garage
    date: date  # Booking Date
    time: time  # Booking Time
    status: BookingStatus = BookingStatus.Pending # Default status to 'Pending'

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BookingBase):
    pass

class Booking(BookingBase):
    id: int  # Booking ID

    class Config:
        from_attributes = True  # Replaced 'orm_mode' with 'from_attributes'

# Quote Schema
class QuoteBase(BaseModel):
    amount: int  # Quote Amount
    status: str = "Pending"  # Default status to 'Pending'

class QuoteCreate(QuoteBase):
    pass

class QuoteUpdate(QuoteBase):
    pass

class Quote(QuoteBase):
    id: int
    booking_id: int  # Booking ID relation

    class Config:
        from_attributes = True  # Replaced 'orm_mode' with 'from_attributes'
