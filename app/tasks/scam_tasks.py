from app.core.celery_app import celery_app
from app.core.database import SessionLocal
from app.models.submission import ScamSubmission
from app.models.ai_report import AIReport
from app.services.ml_service import predict
from app.services.ai_agent import classify_scam
from app.core.logger import logger


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def process_submission_task(self, submission_id: int, message: str):
    """
    Celery task — runs in background worker.

    This is the ASYNCHRONOUS part of the flow:
    1. ML model predicts SCAM / NOT_SCAM
    2. Gemini AI classifies scam type
    3. Creates AIReport in database
    4. Marks submission as REVIEWED

    If it fails → automatically retries up to 3 times.
    """
    db = SessionLocal()
    try:
        logger.info(f"[CELERY] Processing submission {submission_id}")

        # Step 1 — ML prediction
        prediction, confidence = predict(message)
        logger.info(f"[CELERY] ML result: {prediction} ({confidence:.2f})")

        # Step 2 — Gemini AI classification
        ai_result = classify_scam(message)
        logger.info(f"[CELERY] Gemini result: {ai_result}")

        # Step 3 — Check if report already exists
        existing = db.query(AIReport).filter(
            AIReport.submission_id == submission_id
        ).first()

        if existing:
            existing.prediction     = prediction
            existing.confidence     = confidence
            existing.scam_type      = ai_result.get("scam_type", "OTHER")
            existing.risk_score     = ai_result.get("risk_score", 5)
            existing.reason         = ai_result.get("reason", "")
            existing.recommendation = ai_result.get("recommendation", "")
            existing.generated_by   = "AI"
            existing.status         = "PUBLISHED"
        else:
            report = AIReport(
                submission_id   = submission_id,
                prediction      = prediction,
                confidence      = confidence,
                scam_type       = ai_result.get("scam_type", "OTHER"),
                risk_score      = ai_result.get("risk_score", 5),
                reason          = ai_result.get("reason", ""),
                recommendation  = ai_result.get("recommendation", ""),
                generated_by    = "AI",
                status          = "PUBLISHED"
            )
            db.add(report)

        # Step 4 — Mark submission as REVIEWED
        submission = db.query(ScamSubmission).filter(
            ScamSubmission.id == submission_id
        ).first()
        if submission:
            submission.status = "REVIEWED"

        db.commit()
        logger.info(f"[CELERY] Submission {submission_id} completed successfully")

    except Exception as e:
        logger.error(f"[CELERY] Failed processing submission {submission_id}: {e}")
        db.rollback()

        # Mark as failed
        try:
            submission = db.query(ScamSubmission).filter(
                ScamSubmission.id == submission_id
            ).first()
            if submission:
                submission.status = "FAILED"
                db.commit()
        except Exception:
            pass

        # Retry the task automatically
        raise self.retry(exc=e, countdown=60)

    finally:
        db.close()
        