from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import User
from ..deps import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def ensure_admin(user_payload):
    if user_payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

@router.patch("/users/{user_id}/activate")
def activate_user(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_admin(user)
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, detail="User not found")
    u.is_active = True
    db.commit()
    return {"user_id": user_id, "is_active": True}

@router.patch("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    ensure_admin(user)
    u = db.query(User).get(user_id)
    if not u:
        raise HTTPException(404, detail="User not found")
    u.is_active = False
    db.commit()
    return {"user_id": user_id, "is_active": False}
