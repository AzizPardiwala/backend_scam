import pytest
from unittest.mock import patch
from app.services.background_tasks import process_submission
from app.models.submission import ScamSubmission


class TestBackgroundTask:

    def test_report_status_becomes_verified(self, db, regular_user):
        sub = ScamSubmission(user_id=regular_user.id, message="Fake lottery", status="PENDING")
        db.add(sub)
        db.commit()
        sub_id = sub.id

        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.92)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "LOTTERY_SCAM", "risk_score": 9,
                 "reason": "Classic lottery fraud", "recommendation": "Ignore it"
             }):
            with patch.object(db, 'close', return_value=None):
                process_submission(db, sub_id, "Fake lottery")

        db.expire_all()
        updated = db.query(ScamSubmission).filter(ScamSubmission.id == sub_id).first()
        assert updated.status == "REVIEWED"

    def test_report_ml_fields_populated(self, db, regular_user):
        from app.models.ai_report import AIReport
        sub = ScamSubmission(user_id=regular_user.id, message="test", status="PENDING")
        db.add(sub)
        db.commit()
        sub_id = sub.id

        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.88)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "UPI_FRAUD", "risk_score": 7,
                 "reason": "UPI scam pattern", "recommendation": "Block the number"
             }):
            with patch.object(db, 'close', return_value=None):
                process_submission(db, sub_id, "test")

        db.expire_all()
        from app.models.ai_report import AIReport
        report = db.query(AIReport).filter(AIReport.submission_id == sub_id).first()
        assert report is not None
        assert report.prediction == "SCAM"
        assert report.confidence == 0.88
        assert report.scam_type == "UPI_FRAUD"
        assert report.risk_score == 7

    def test_report_marked_failed_on_error(self, db, regular_user):
        sub = ScamSubmission(user_id=regular_user.id, message="test", status="PENDING")
        db.add(sub)
        db.commit()
        sub_id = sub.id

        with patch("app.services.background_tasks.predict", side_effect=Exception("ML crashed")):
            with patch.object(db, 'close', return_value=None):
                process_submission(db, sub_id, "test")

        db.expire_all()
        updated = db.query(ScamSubmission).filter(ScamSubmission.id == sub_id).first()
        assert updated.status == "FAILED"

    def test_nonexistent_report_id_doesnt_crash(self, db):
        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.9)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "OTHER", "risk_score": 5,
                 "reason": "unknown", "recommendation": "Be careful"
             }):
            with patch.object(db, 'close', return_value=None):
                process_submission(db, 99999, "some message")