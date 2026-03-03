from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import SessionLocal
from app.models.report import Report
from app.schemas.report_schema import ReportCreate, ReportResponse
from app.services.scam_detector import detect_scam

router = APIRouter(prefix="/reports", tags=["Reports"])

# Database dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# CREATE
@router.post("/", response_model=ReportResponse)
def create_report(report: ReportCreate, db: Session = Depends(get_db)):
    result = detect_scam(report.message)

    new_report = Report(
        message=report.message,
        label=result["label"],
        confidence=result["confidence"]
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    return new_report

# READ ALL
@router.get("/", response_model=List[ReportResponse])
def get_reports(db: Session = Depends(get_db)):
    return db.query(Report).all()

# READ ONE
@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report

# UPDATE
@router.put("/{report_id}", response_model=ReportResponse)
def update_report(report_id: int, report: ReportCreate, db: Session = Depends(get_db)):
    existing = db.query(Report).filter(Report.id == report_id).first()

    if not existing:
        raise HTTPException(status_code=404, detail="Report not found")

    result = detect_scam(report.message)

    existing.message = report.message
    existing.label = result["label"]
    existing.confidence = result["confidence"]

    db.commit()
    db.refresh(existing)
    return existing

# DELETE
@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db)):
    report = db.query(Report).filter(Report.id == report_id).first()

    if not report:
        raise HTTPException(status_code=404, detail="Report not found")

    db.delete(report)
    db.commit()
    return {"message": "Deleted successfully"}