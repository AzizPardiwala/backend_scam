from sqlalchemy.orm import Session
from app.models.scam_report import ScamReport
from app.services.ml_service import predict


def process_scam(db: Session, scam_id: int, text: str):
    prediction, confidence = predict(text)

    scam = db.query(ScamReport).filter(ScamReport.id == scam_id).first()

    if scam:
        scam.prediction = prediction
        scam.confidence = confidence
        scam.status = "VERIFIED"

        db.commit()