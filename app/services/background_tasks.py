from sqlalchemy.orm import Session
from app.models.scam_report import ScamReport
from app.services.ml_service import predict
from app.services.ai_agent import classify_scam
from app.core.logger import logger


def process_scam_report(db: Session, scam_id: int, message: str):
    """
    ASYNCHRONOUS background task — runs AFTER the API has already
    returned "Processing" to the user.

    Steps:
    1. ML model predicts SCAM / NOT_SCAM + confidence  (fast, local)
    2. Gemini classifies scam type + risk score + reason (external API)
    3. Updates DB record and sets status to VERIFIED
    """
    try:
        logger.info(f"[BG] Starting processing for report {scam_id}")

        prediction, confidence = predict(message)
        logger.info(f"[BG] ML result for {scam_id}: {prediction} ({confidence:.2f})")

        ai_result = classify_scam(message)
        logger.info(f"[BG] Gemini result for {scam_id}: {ai_result}")

        scam = db.query(ScamReport).filter(ScamReport.id == scam_id).first()
        if scam:
            scam.prediction = prediction
            scam.confidence = confidence
            scam.scam_type = ai_result.get("scam_type", "OTHER")
            scam.risk_score = ai_result.get("risk_score", 5)
            scam.reason = ai_result.get("reason", "")
            scam.status = "VERIFIED"
            db.commit()
            logger.info(f"[BG] Report {scam_id} updated to VERIFIED")

    except Exception as e:
        logger.error(f"[BG] Failed processing report {scam_id}: {e}")
        try:
            scam = db.query(ScamReport).filter(ScamReport.id == scam_id).first()
            if scam:
                scam.status = "FAILED"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()