from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db, SessionLocal
from app.models.scam_report import ScamReport
from app.core.deps import get_current_user
from app.schemas.report_schema import ReportCreate, ReportUpdate, ReportResponse
from app.services.background_tasks import process_scam_report
from typing import List

router = APIRouter(prefix="/scam", tags=["Scam"])


@router.post("/report", response_model=ReportResponse, status_code=status.HTTP_202_ACCEPTED)
async def submit_report(
    data: ReportCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Submit a scam report. Saves instantly (sync), AI runs in background (async)."""
    scam = ScamReport(user_id=user.id, message=data.message, status="PENDING")
    db.add(scam)
    db.commit()
    db.refresh(scam)

    bg_db = SessionLocal()
    background_tasks.add_task(process_scam_report, bg_db, scam.id, data.message)
    return scam


@router.get("/my-reports", response_model=List[ReportResponse])
def get_my_reports(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get all reports by the logged-in user."""
    return db.query(ScamReport).filter(
        ScamReport.user_id == user.id
    ).order_by(ScamReport.created_at.desc()).all()


@router.get("/search/query", response_model=List[ReportResponse])
def search_scams(q: str, db: Session = Depends(get_db)):
    """Public search across verified scam reports."""
    return db.query(ScamReport).filter(
        ScamReport.message.ilike(f"%{q}%"),
        ScamReport.status == "VERIFIED"
    ).order_by(ScamReport.created_at.desc()).limit(50).all()


@router.get("/{report_id}", response_model=ReportResponse)
def get_report(report_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Get a specific report (only owner can view)."""
    scam = db.query(ScamReport).filter(
        ScamReport.id == report_id, ScamReport.user_id == user.id
    ).first()
    if not scam:
        raise HTTPException(status_code=404, detail="Report not found or access denied")
    return scam


@router.put("/{report_id}", response_model=ReportResponse)
async def update_report(
    report_id: int,
    data: ReportUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Update a report and re-run AI analysis."""
    scam = db.query(ScamReport).filter(
        ScamReport.id == report_id, ScamReport.user_id == user.id
    ).first()
    if not scam:
        raise HTTPException(status_code=404, detail="Report not found or access denied")

    scam.message = data.message
    scam.status = "PENDING"
    scam.prediction = None
    scam.confidence = None
    scam.scam_type = None
    scam.risk_score = None
    scam.reason = None
    db.commit()
    db.refresh(scam)

    bg_db = SessionLocal()
    background_tasks.add_task(process_scam_report, bg_db, scam.id, data.message)
    return scam


@router.delete("/{report_id}")
def delete_report(report_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Delete own report."""
    scam = db.query(ScamReport).filter(
        ScamReport.id == report_id, ScamReport.user_id == user.id
    ).first()
    if not scam:
        raise HTTPException(status_code=404, detail="Report not found or access denied")
    db.delete(scam)
    db.commit()
    return {"message": f"Report {report_id} deleted successfully"}