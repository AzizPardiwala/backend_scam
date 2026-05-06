from sqlalchemy.orm import Session
from app.models.submission import ScamSubmission
from app.models.ai_report import AIReport
from app.services.ml_service import predict
from app.services.ai_agent import classify_scam
from app.core.logger import logger


def process_submission(db: Session, submission_id: int, message: str):
    """
    ASYNCHRONOUS background task.
    Runs AFTER the API has already returned 202 to the user.

    Steps:
      1. ML model  → SCAM / NOT_SCAM + confidence   (fast, local)
      2. Gemini AI → scam_type, risk_score, reason   (external API)
      3. Creates an AIReport record linked to the submission
      4. Marks the submission status as REVIEWED
    """
    try:
        logger.info(f"[BG] Processing submission {submission_id}")

        # Step 1 — ML prediction (synchronous, local model)
        prediction, confidence = predict(message)
        logger.info(f"[BG] ML result for {submission_id}: {prediction} ({confidence:.2f})")

        # Step 2 — Gemini AI classification (synchronous call to external API)
        ai_result = classify_scam(message)
        logger.info(f"[BG] Gemini result for {submission_id}: {ai_result}")

        # Step 3 — Check if a report already exists (re-analysis case)
        existing = db.query(AIReport).filter(
            AIReport.submission_id == submission_id
        ).first()

        if existing:
            # Update existing report
            existing.prediction     = prediction
            existing.confidence     = confidence
            existing.scam_type      = ai_result.get("scam_type", "OTHER")
            existing.risk_score     = ai_result.get("risk_score", 5)
            existing.reason         = ai_result.get("reason", "")
            existing.recommendation = ai_result.get("recommendation", "")
            existing.generated_by   = "AI"
            existing.status         = "PUBLISHED"
        else:
            # Create new report
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
        logger.info(f"[BG] Submission {submission_id} marked REVIEWED, report created/updated")

    except Exception as e:
        logger.error(f"[BG] Failed processing submission {submission_id}: {e}")
        try:
            submission = db.query(ScamSubmission).filter(
                ScamSubmission.id == submission_id
            ).first()
            if submission:
                submission.status = "FAILED"
                db.commit()
        except Exception:
            pass
    finally:
        db.close()