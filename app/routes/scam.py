from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.scam_detector import detect_scam
from app.schemas.report_schema import ReportCreate, ReportResponse
from app.models.report import Report
from app.core.database import SessionLocal

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/detect", response_model=ReportResponse)
def detect(data: ReportCreate, db: Session = Depends(get_db)):
    result = detect_scam(data.message)

    report = Report(
        message=data.message,
        label=result["label"],
        confidence=result["confidence"],
        reason=result["reason"],
        type=result["type"],
        created_at=datetime.utcnow()
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return report