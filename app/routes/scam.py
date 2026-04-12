from fastapi import APIRouter
from datetime import datetime

from app.services.scam_detector import detect_scam
from app.schemas.report_schema import ReportCreate, ReportResponse
from app.routes.report import reports_db   # ✅ important

router = APIRouter()

@router.post("/detect", response_model=ReportResponse)
def detect(message: ReportCreate):

    result = detect_scam(message.message)

    response = {
        "id": int(datetime.now().timestamp()),
        "message": message.message,
        "label": result["label"],
        "confidence": result["confidence"],
        "reason": result["reason"],
        "type": result["type"],
        "created_at": datetime.now()
    }

    # ✅ SAVE TO REPORTS
    reports_db.append(response)

    return response