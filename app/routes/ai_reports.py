from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db, SessionLocal
from app.core.deps import get_current_user, admin_required
from app.models.ai_report import AIReport
from app.models.submission import ScamSubmission
from app.schemas.ai_report_schema import AIReportAdminUpdate, AIReportResponse
from app.services.background_tasks import process_submission

router = APIRouter(prefix="/ai-reports", tags=["AI Reports"])


# ─────────────────────────────────────────────────────────────
# GET /ai-reports                          [ADMIN ONLY]
# Admin views all AI reports with filters.
# ─────────────────────────────────────────────────────────────
@router.get("/", response_model=List[AIReportResponse])
def get_all_reports(
    status: Optional[str] = None,
    scam_type: Optional[str] = None,
    prediction: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """
    Admin: Get all AI-generated reports.
    Optional filters: status, scam_type, prediction.
    """
    query = db.query(AIReport)

    if status:
        query = query.filter(AIReport.status == status.upper())
    if scam_type:
        query = query.filter(AIReport.scam_type == scam_type.upper())
    if prediction:
        query = query.filter(AIReport.prediction == prediction.upper())

    return query.order_by(AIReport.created_at.desc()).offset(offset).limit(limit).all()


# ─────────────────────────────────────────────────────────────
# GET /ai-reports/{id}                     [ADMIN ONLY]
# Admin views a specific AI report.
# ─────────────────────────────────────────────────────────────
@router.get("/{report_id}", response_model=AIReportResponse)
def get_report(
    report_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """Admin: View any specific AI report by ID."""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    return report


# ─────────────────────────────────────────────────────────────
# PUT /ai-reports/{id}                     [ADMIN ONLY]
# Admin overrides/edits an AI-generated report.
# ─────────────────────────────────────────────────────────────
@router.put("/{report_id}", response_model=AIReportResponse)
def update_report(
    report_id: int,
    data: AIReportAdminUpdate,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """
    Admin: Edit/override any field of an AI report.
    Only the fields you send will be updated (partial update).
    Sets generated_by to ADMIN to show it was human-reviewed.
    """
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    # Only update fields that were actually sent (partial update)
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(report, field, value)

    # Mark as human-reviewed
    report.generated_by = "ADMIN"
    db.commit()
    db.refresh(report)
    return report


# ─────────────────────────────────────────────────────────────
# DELETE /ai-reports/{id}                  [ADMIN ONLY]
# Admin deletes an AI report.
# ─────────────────────────────────────────────────────────────
@router.delete("/{report_id}", status_code=status.HTTP_200_OK)
def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """Admin: Delete an AI report. Submission stays, only the report is removed."""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")

    # Reset the submission status back to PENDING
    sub = db.query(ScamSubmission).filter(
        ScamSubmission.id == report.submission_id
    ).first()
    if sub:
        sub.status = "PENDING"

    db.delete(report)
    db.commit()
    return {"message": f"Report {report_id} deleted. Submission reset to PENDING."}


# ─────────────────────────────────────────────────────────────
# POST /ai-reports/generate/{submission_id}  [ADMIN ONLY]
# Admin manually triggers AI re-analysis on a submission.
# ─────────────────────────────────────────────────────────────
@router.post("/generate/{submission_id}", status_code=status.HTTP_202_ACCEPTED)
async def regenerate_report(
    submission_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """
    Admin: Manually trigger AI re-analysis on any submission.
    Useful when AI failed or admin wants a fresh analysis.
    Runs asynchronously — returns immediately, report updates in background.
    """
    sub = db.query(ScamSubmission).filter(ScamSubmission.id == submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail=f"Submission {submission_id} not found")

    sub.status = "PENDING"
    db.commit()

    bg_db = SessionLocal()
    background_tasks.add_task(process_submission, bg_db, submission_id, sub.message)

    return {
        "message": f"AI re-analysis triggered for submission {submission_id}",
        "status": "processing"
    }


# ─────────────────────────────────────────────────────────────
# POST /ai-reports/{id}/publish             [ADMIN ONLY]
# Admin publishes a draft report so users can see it.
# ─────────────────────────────────────────────────────────────
@router.post("/{report_id}/publish", status_code=status.HTTP_200_OK)
def publish_report(
    report_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """Admin: Publish a report (makes it visible to the user)."""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    report.status = "PUBLISHED"
    db.commit()
    return {"message": f"Report {report_id} published"}


# ─────────────────────────────────────────────────────────────
# POST /ai-reports/{id}/reject              [ADMIN ONLY]
# Admin rejects a report (marks submission as not a scam).
# ─────────────────────────────────────────────────────────────
@router.post("/{report_id}/reject", status_code=status.HTTP_200_OK)
def reject_report(
    report_id: int,
    db: Session = Depends(get_db),
    admin=Depends(admin_required)
):
    """Admin: Reject a report (mark as not a genuine scam)."""
    report = db.query(AIReport).filter(AIReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail=f"Report {report_id} not found")
    report.status = "REJECTED"
    db.commit()
    return {"message": f"Report {report_id} rejected"}
