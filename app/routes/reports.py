from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.scam_report import ScamReport
from app.schemas.report_schema import ReportResponse
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/", response_model=List[ReportResponse])
def get_public_reports(limit: int = 50, offset: int = 0, db: Session = Depends(get_db)):
    """Public feed — returns only VERIFIED scam reports. No login needed."""
    return db.query(ScamReport).filter(
        ScamReport.status == "VERIFIED"
    ).order_by(ScamReport.created_at.desc()).offset(offset).limit(limit).all()