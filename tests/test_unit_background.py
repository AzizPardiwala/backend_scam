"""
UNIT TESTS — Background task (ML + AI processing pipeline)
Tests the process_scam_report function directly without HTTP
"""
import pytest
from unittest.mock import patch
from app.services.background_tasks import process_scam_report
from app.models.scam_report import ScamReport


class TestBackgroundTask:

    def test_report_status_becomes_verified(self, db, regular_user):
        report = ScamReport(user_id=regular_user.id, message="Fake lottery", status="PENDING")
        db.add(report)
        db.commit()
        report_id = report.id

        # Pass the SAME test db session to background task — not a new SessionLocal
        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.92)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "LOTTERY_SCAM", "risk_score": 9, "reason": "Classic lottery fraud"
             }):
            # Temporarily disable db.close() in finally block so test db stays open
            with patch.object(db, 'close', return_value=None):
                process_scam_report(db, report_id, "Fake lottery")

        db.expire_all()
        updated = db.query(ScamReport).filter(ScamReport.id == report_id).first()
        assert updated.status == "VERIFIED"

    def test_report_ml_fields_populated(self, db, regular_user):
        report = ScamReport(user_id=regular_user.id, message="test", status="PENDING")
        db.add(report)
        db.commit()
        report_id = report.id

        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.88)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "UPI_FRAUD", "risk_score": 7, "reason": "UPI scam pattern"
             }):
            with patch.object(db, 'close', return_value=None):
                process_scam_report(db, report_id, "test")

        db.expire_all()
        updated = db.query(ScamReport).filter(ScamReport.id == report_id).first()
        assert updated.prediction == "SCAM"
        assert updated.confidence == 0.88
        assert updated.scam_type == "UPI_FRAUD"
        assert updated.risk_score == 7

    def test_report_marked_failed_on_error(self, db, regular_user):
        report = ScamReport(user_id=regular_user.id, message="test", status="PENDING")
        db.add(report)
        db.commit()
        report_id = report.id

        with patch("app.services.background_tasks.predict", side_effect=Exception("ML crashed")):
            with patch.object(db, 'close', return_value=None):
                process_scam_report(db, report_id, "test")

        db.expire_all()
        updated = db.query(ScamReport).filter(ScamReport.id == report_id).first()
        assert updated.status == "FAILED"

    def test_nonexistent_report_id_doesnt_crash(self, db):
        with patch("app.services.background_tasks.predict", return_value=("SCAM", 0.9)), \
             patch("app.services.background_tasks.classify_scam", return_value={
                 "scam_type": "OTHER", "risk_score": 5, "reason": "unknown"
             }):
            with patch.object(db, 'close', return_value=None):
                process_scam_report(db, 99999, "some message")  # Should not crash