from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.core.database import get_db
from app.models.user import User
from app.core.security import hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Auth"])


# =========================
# 📌 REQUEST MODELS
# =========================

class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# ✅ REGISTER API
# =========================

@router.post("/register")
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    user = User(
        email=data.email,
        password=hash_password(data.password),
        name=data.name,
        role="user"
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User created successfully",
        "user_id": user.id
    }


# =========================
# 🔐 LOGIN API
# =========================

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    # Check if user exists
    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    # Verify password
    if not verify_password(data.password, user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    return {
        "message": "Login successful",
        "user_id": user.id,
        "email": user.email
    }