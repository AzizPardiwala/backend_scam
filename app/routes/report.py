from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import SessionLocal
from app.models.report import Report
from app.schemas.report_schema import ReportResponse, ReportCreate
from app.services.scam_detector import detect_scam
from app.core.security import get_current_user  # ✅ protect

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# 🔒 GET ALL (PROTECTED)
@router.get("/", response_model=List[ReportResponse])
def get_reports(
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    return db.query(Report).all()

# 🔒 UPDATE (PROTECTED)
@router.put("/{id}", response_model=ReportResponse)
def update_report(
    id: int,
    data: ReportCreate,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    result = detect_scam(data.message)

    report.message = data.message
    report.label = result["label"]
    report.confidence = result["confidence"]
    report.reason = result["reason"]
    report.type = result["type"]
    report.created_at = datetime.utcnow()

    db.commit()
    db.refresh(report)

    return report

# 🔒 DELETE (PROTECTED)
@router.delete("/{id}")
def delete_report(
    id: int,
    db: Session = Depends(get_db),
    user: str = Depends(get_current_user)
):
    report = db.query(Report).filter(Report.id == id).first()

    if report:
        db.delete(report)
        db.commit()
        return {"msg": "deleted"}

    raise HTTPException(status_code=404, detail="Report not found")