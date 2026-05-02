from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.scam_report import ScamReport
from app.core.deps import get_current_user
from app.services.background_tasks import process_scam

router = APIRouter(prefix="/scam", tags=["Scam"])


# 🔥 POST: User submits scam
@router.post("/detect")
async def detect_scam(
    message: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    scam = ScamReport(
        message=message,
        user_id=user.id,
        status="PENDING"
    )

    db.add(scam)
    db.commit()
    db.refresh(scam)

    # Run ML in background
    new_db = SessionLocal()
    background_tasks.add_task(process_scam, new_db, scam.id, message)

    return {
        "id": scam.id,
        "status": "Processing"
    }


# 🔍 GET: Search scams (public)
@router.get("/search")
def search_scams(q: str, db: Session = Depends(get_db)):
    scams = db.query(ScamReport).filter(
        ScamReport.message.ilike(f"%{q}%")
    ).all()

    return scams


# ⚡ POST: Admin verify manually (optional advanced API)
@router.post("/{id}/verify")
def verify_scam(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    scam = db.query(ScamReport).filter(ScamReport.id == id).first()

    if not scam:
        return {"error": "Not found"}

    scam.status = "VERIFIED"
    db.commit()

    return {"message": "Verified manually"}