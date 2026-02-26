from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.services.scam_detector import detect_scam
from app.models.scam_report import ScamReport

router = APIRouter()

@router.post("/analyze")
def analyze_message(message: str, db: Session = Depends(get_db)):

    result = detect_scam(message)

    report = ScamReport(
        message=message,
        label=result["label"],
        score=result["score"]
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return result


@router.get("/reports")
def get_reports(db: Session = Depends(get_db)):
    reports = db.query(ScamReport).all()
    return reports