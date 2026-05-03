from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


# ✅ Get current logged-in user
@router.get("/me")
def get_me(user=Depends(get_current_user)):
    return user


# ✅ Update user (only user can update)
@router.put("/update")
def update_user(
    name: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    user.name = name
    db.commit()
    db.refresh(user)
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role, "is_active": user.is_active, "created_at": user.created_at}


# ✅ Delete user (soft delete)
@router.delete("/delete")
def delete_user(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    user.is_active = False
    db.commit()
    return {"message": "User deleted"}