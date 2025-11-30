from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, schemas, crud, database, services
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI instance
app = FastAPI(title="MOT & Services API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

database.init_db()

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Booking and Quote Service instances
from .services.booking_service import BookingService  # Corrected import
from .services.booking_service import QuoteService    # Corrected import

booking_service = BookingService
quote_service = QuoteService

# Routes for Booking
@app.post("/bookings/", response_model=schemas.Booking)
async def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    return booking_service(db).create_booking(booking)

@app.get("/bookings/", response_model=list[schemas.Booking])
async def get_bookings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return booking_service(db).get_bookings(skip=skip, limit=limit)

@app.get("/bookings_requests/", response_model=list[schemas.Booking])
async def get_bookings_by_status(skip: int = 0, limit: int = 10, status: str = "Pending", db: Session = Depends(get_db)):
    return booking_service(db).get_bookings_by_status(skip=skip, limit=limit, status=status)

@app.get("/bookings/{registration_number}", response_model=schemas.Booking)
async def get_booking_by_registration_number(registration_number: str, db: Session = Depends(get_db)):
    db_booking = booking_service(db).get_booking_by_registration(registration_number)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.put("/bookings/{registration_number}", response_model=schemas.Booking)
async def update_booking(registration_number: str, updated_booking: schemas.BookingUpdate, db: Session = Depends(get_db)):
    db_booking = booking_service(db).update_booking(registration_number, updated_booking)
    if db_booking is None:
        raise HTTPException(status_code=404, detail="Booking not found")
    return db_booking

@app.delete("/bookings/{registration_number}")
async def delete_booking(registration_number: str, db: Session = Depends(get_db)):
    return booking_service(db).delete_booking(registration_number)

@app.put("/bookings/{booking_id}/status", response_model=schemas.Booking)
async def update_booking_status(
    booking_id: int,
    status_update: schemas.BookingStatusUpdate,
    db: Session = Depends(get_db)
):
    updated_booking = booking_service(db).update_status(booking_id, status_update.status)

    if not updated_booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    return updated_booking


# Routes for Quote
@app.post("/quotes/", response_model=schemas.Quote)
async def create_quote(quote: schemas.QuoteCreate, booking_id: int, db: Session = Depends(get_db)):
    return quote_service(db).create_quote(quote, booking_id)

@app.get("/quotes/{booking_id}", response_model=schemas.Quote)
async def get_quote_by_booking_id(booking_id: int, db: Session = Depends(get_db)):
    db_quote = quote_service(db).get_quote_by_booking_id(booking_id)
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return db_quote

@app.put("/quotes/{booking_id}", response_model=schemas.Quote)
async def update_quote(booking_id: int, updated_quote: schemas.QuoteUpdate, db: Session = Depends(get_db)):
    db_quote = quote_service(db).update_quote(booking_id, updated_quote)
    if db_quote is None:
        raise HTTPException(status_code=404, detail="Quote not found")
    return db_quote

@app.delete("/quotes/{booking_id}")
async def delete_quote(booking_id: int, db: Session = Depends(get_db)):
    return quote_service(db).delete_quote(booking_id)
