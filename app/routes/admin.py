from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.scam_report import ScamReport
from app.models.user import User
from app.core.deps import admin_required
from app.schemas.report_schema import ReportResponse
from typing import List, Optional

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/reports", response_model=List[ReportResponse])
def get_all_reports(
    status: Optional[str] = None,
    scam_type: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """Admin: Get all reports. Filter by status or scam_type."""
    query = db.query(ScamReport)
    if status:
        query = query.filter(ScamReport.status == status.upper())
    if scam_type:
        query = query.filter(ScamReport.scam_type == scam_type.upper())
    return query.order_by(ScamReport.created_at.desc()).offset(offset).limit(limit).all()


@router.get("/reports/{report_id}", response_model=ReportResponse)
def get_report_by_id(report_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: View any specific report."""
    scam = db.query(ScamReport).filter(ScamReport.id == report_id).first()
    if not scam:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return scam


@router.delete("/reports/{report_id}")
def delete_any_report(report_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: Delete any report."""
    scam = db.query(ScamReport).filter(ScamReport.id == report_id).first()
    if not scam:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    db.delete(scam)
    db.commit()
    return {"message": f"Report {report_id} deleted by admin"}


@router.post("/reports/{report_id}/verify")
def manually_verify(report_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: Manually mark a report as VERIFIED."""
    scam = db.query(ScamReport).filter(ScamReport.id == report_id).first()
    if not scam:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    scam.status = "VERIFIED"
    db.commit()
    return {"message": f"Report {report_id} manually verified"}


@router.post("/reports/{report_id}/reject")
def reject_report(report_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: Reject a false report."""
    scam = db.query(ScamReport).filter(ScamReport.id == report_id).first()
    if not scam:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    scam.status = "REJECTED"
    db.commit()
    return {"message": f"Report {report_id} rejected"}


@router.get("/users")
def get_all_users(db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: View all users."""
    users = db.query(User).all()
    return [
        {"id": u.id, "email": u.email, "name": u.name,
         "role": u.role, "is_active": u.is_active, "created_at": u.created_at}
        for u in users
    ]


@router.post("/users/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db), admin=Depends(admin_required)):
    """Admin: Deactivate a user account."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": f"User {user_id} deactivated"}