from fastapi import APIRouter
from app.schemas.report_schema import ScamRequest, ScamResponse
from app.services.scam_detector import ScamDetector

router = APIRouter(prefix="/scam", tags=["Scam Detection"])

detector = ScamDetector()


@router.post("/detect", response_model=ScamResponse)
def detect_scam(data: ScamRequest):
    result = detector.analyze(data.message)

    return ScamResponse(**result)
