from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.models.scam_report import ScamReport
from app.schemas.report_schema import ScamReportCreate, ScamReportResponse
from app.services.scam_detector import detect_scam

router = APIRouter()


@router.post("/analyze", response_model=ScamReportResponse)
def analyze_message(
    data: ScamReportCreate,
    db: Session = Depends(get_db)
):
    label, score = detect_scam(data.message)

    new_report = ScamReport(
        message=data.message,
        label=label,
        score=score
    )

    db.add(new_report)
    db.commit()
    db.refresh(new_report)

    return new_report


@router.get("/reports", response_model=List[ScamReportResponse])
def get_reports(
    label: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(ScamReport)

    if label:
        query = query.filter(ScamReport.label == label)

    reports = query.order_by(ScamReport.created_at.desc()) \
                   .offset(skip) \
                   .limit(limit) \
                   .all()

    return reports