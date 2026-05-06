from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user
from app.models.submission import ScamSubmission
from app.models.ai_report import AIReport
from app.schemas.submission_schema import SubmissionCreate, SubmissionUpdate, SubmissionResponse
from app.schemas.ai_report_schema import AIReportResponse
from app.services.background_tasks import process_submission

router = APIRouter(prefix="/submissions", tags=["Submissions"])


# ─────────────────────────────────────────────────────────────
# POST /submissions
# User submits a scam report.
# SYNCHRONOUS  → saves to DB instantly, returns 202
# ASYNCHRONOUS → ML + Gemini run in background after response
# ─────────────────────────────────────────────────────────────
@router.post("/", response_model=SubmissionResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_submission(
    data: SubmissionCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Submit a new scam report.
    - Saves instantly (SYNCHRONOUS) → you get a response immediately.
    - AI analysis runs in background (ASYNCHRONOUS) → check back later.
    - Status starts as PENDING, becomes REVIEWED after AI finishes.
    """
    submission = ScamSubmission(
        user_id=user.id,
        message=data.message,
        status="PENDING"
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)

    # Hand off to background — fresh DB session so request session can close
    bg_db = SessionLocal()
    background_tasks.add_task(process_submission, bg_db, submission.id, data.message)

    return submission


# ─────────────────────────────────────────────────────────────
# GET /submissions/mine
# User sees only their own submissions.
# ─────────────────────────────────────────────────────────────
@router.get("/mine", response_model=List[SubmissionResponse])
def get_my_submissions(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Get all submissions by the logged-in user."""
    return db.query(ScamSubmission).filter(
        ScamSubmission.user_id == user.id
    ).order_by(ScamSubmission.created_at.desc()).all()


# ─────────────────────────────────────────────────────────────
# GET /submissions/{id}
# User views a single submission (only their own).
# ─────────────────────────────────────────────────────────────
@router.get("/{submission_id}", response_model=SubmissionResponse)
def get_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """View a specific submission. Users can only view their own."""
    sub = db.query(ScamSubmission).filter(
        ScamSubmission.id == submission_id,
        ScamSubmission.user_id == user.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or access denied")
    return sub


# ─────────────────────────────────────────────────────────────
# PUT /submissions/{id}
# User edits their own submission.
# Re-triggers AI analysis asynchronously.
# ─────────────────────────────────────────────────────────────
@router.put("/{submission_id}", response_model=SubmissionResponse)
async def update_submission(
    submission_id: int,
    data: SubmissionUpdate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    Update submission text.
    - Resets status to PENDING.
    - Re-runs AI analysis in background (ASYNCHRONOUS).
    """
    sub = db.query(ScamSubmission).filter(
        ScamSubmission.id == submission_id,
        ScamSubmission.user_id == user.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or access denied")

    # Update text and reset status for re-analysis
    sub.message = data.message
    sub.status = "PENDING"
    db.commit()
    db.refresh(sub)

    # Re-run AI asynchronously
    bg_db = SessionLocal()
    background_tasks.add_task(process_submission, bg_db, sub.id, data.message)

    return sub


# ─────────────────────────────────────────────────────────────
# DELETE /submissions/{id}
# User deletes their own submission + linked AI report.
# ─────────────────────────────────────────────────────────────
@router.delete("/{submission_id}", status_code=status.HTTP_200_OK)
def delete_submission(
    submission_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """Delete a submission and its linked AI report."""
    sub = db.query(ScamSubmission).filter(
        ScamSubmission.id == submission_id,
        ScamSubmission.user_id == user.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or access denied")

    # Delete linked AI report first (foreign key)
    db.query(AIReport).filter(AIReport.submission_id == submission_id).delete()
    db.delete(sub)
    db.commit()
    return {"message": f"Submission {submission_id} and its report deleted"}


# ─────────────────────────────────────────────────────────────
# GET /submissions/{id}/report
# User views the AI report for their submission.
# ─────────────────────────────────────────────────────────────
@router.get("/{submission_id}/report", response_model=AIReportResponse)
def get_my_report(
    submission_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    """
    View the AI-generated report for your submission.
    Returns 404 if AI hasn't finished yet (still PENDING).
    """
    # Verify ownership first
    sub = db.query(ScamSubmission).filter(
        ScamSubmission.id == submission_id,
        ScamSubmission.user_id == user.id
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found or access denied")

    report = db.query(AIReport).filter(AIReport.submission_id == submission_id).first()
    if not report:
        raise HTTPException(
            status_code=404,
            detail="Report not ready yet. AI is still processing. Try again in a moment."
        )
    return report
