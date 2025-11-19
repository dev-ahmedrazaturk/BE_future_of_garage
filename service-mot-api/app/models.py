from sqlalchemy import Column, ForeignKey, Integer, String, Date, Time, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from .database import Base

# Enum for booking status
class BookingStatus(PyEnum):
    pending = "Pending"
    approved = "Approved"
    rejected = "Rejected"
    completed = "Completed"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)  # Client name
    vehicle = Column(String)  # General vehicle information
    vehicle_make = Column(String)  # Vehicle Make
    vehicle_model = Column(String)  # Vehicle Model
    vehicle_year = Column(Integer)  # Vehicle Year
    vehicle_reg_number = Column(String, unique=True, index=True)  # Vehicle Registration Number
    engine_size = Column(String)  # Engine Size
    fuel_type = Column(String)  # Fuel Type
    transmission = Column(String)  # Transmission Type
    mileage = Column(Integer)  # Mileage
    additional_notes = Column(String)  # Additional Notes
    selected_garage = Column(String)  # Selected Garage
    date = Column(Date)  # Booking Date
    time = Column(Time)  # Booking Time
    status = Column(Enum(BookingStatus), default=BookingStatus.pending)  # Booking Status

    # Relationship with Quote
    quote = relationship("Quote", back_populates="booking", uselist=False)


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Integer)  # Quote amount
    booking_id = Column(Integer, ForeignKey("bookings.id"))
    status = Column(String, default="Pending")

    # Back relationship to Booking
    booking = relationship("Booking", back_populates="quote")
