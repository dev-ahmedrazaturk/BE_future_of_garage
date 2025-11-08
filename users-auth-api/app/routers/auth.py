import os, sys
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

# Make shared importable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from shared.jwt_utils import create_access_token  # noqa: E402

from ..database import SessionLocal
from ..models import User
from ..schemas import RegisterIn, LoginIn, TokenOut, UserOut
from ..deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=TokenOut, status_code=201)
def register(payload: RegisterIn, db: Session = Depends(get_db)):
    role = payload.role.lower().strip()
    if role not in {"buyer", "seller", "admin"}:
        raise HTTPException(status_code=400, detail="Invalid role. Use buyer, seller, or admin.")

    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered.")

    user = User(
        email=payload.email,
        password_hash=bcrypt.hash(payload.password),
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role}, expires_delta=60)
    return {"access_token": token}

@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not bcrypt.verify(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="User is deactivated")

    token = create_access_token({"sub": str(user.id), "email": user.email, "role": user.role}, expires_delta=60)
    return {"access_token": token}

@router.get("/me", response_model=UserOut)
def me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(User).get(int(user["sub"]))
    if not db_user:
        raise HTTPException(404, detail="User not found")
    return db_user
