"""
INTEGRATION TESTS — Scam routes
Tests: submit, view, update, delete own reports
"""
import pytest
from unittest.mock import patch


class TestSubmitReport:

    def test_submit_report_success(self, client, user_headers):
        with patch("app.routes.scam.process_scam_report"):
            res = client.post("/scam/report",
                json={"message": "Someone asked me to send money via UPI"},
                headers=user_headers
            )
        assert res.status_code == 202
        data = res.json()
        assert data["status"] == "PENDING"
        assert data["message"] == "Someone asked me to send money via UPI"
        assert "id" in data

    def test_submit_report_no_auth(self, client):
        res = client.post("/scam/report", json={"message": "test scam"})
        assert res.status_code == 401

    def test_submit_report_empty_message(self, client, user_headers):
        res = client.post("/scam/report", json={}, headers=user_headers)
        assert res.status_code == 422

    def test_submit_report_creates_in_db(self, client, user_headers, db):
        from app.models.scam_report import ScamReport
        with patch("app.routes.scam.process_scam_report"):
            client.post("/scam/report",
                json={"message": "Lottery fraud call"},
                headers=user_headers
            )
        report = db.query(ScamReport).first()
        assert report is not None
        assert report.message == "Lottery fraud call"

    def test_submit_report_starts_as_pending(self, client, user_headers):
        with patch("app.routes.scam.process_scam_report"):
            res = client.post("/scam/report",
                json={"message": "Fake job offer"},
                headers=user_headers
            )
        assert res.json()["status"] == "PENDING"


class TestGetMyReports:

    def test_get_my_reports_success(self, client, user_headers, sample_report):
        res = client.get("/scam/my-reports", headers=user_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert len(res.json()) == 1

    def test_get_my_reports_no_auth(self, client):
        res = client.get("/scam/my-reports")
        assert res.status_code == 401

    def test_get_my_reports_only_own(self, client, db, sample_report):
        from app.models.user import User
        from app.models.scam_report import ScamReport
        from app.core.security import hash_password, create_access_token

        user2 = User(email="other@test.com", password=hash_password("pass"), name="Other")
        db.add(user2)
        db.commit()
        db.refresh(user2)

        report2 = ScamReport(user_id=user2.id, message="Other user scam", status="PENDING")
        db.add(report2)
        db.commit()

        token2 = create_access_token({"user_id": user2.id, "role": "user"})
        res = client.get("/scam/my-reports", headers={"Authorization": f"Bearer {token2}"})

        assert len(res.json()) == 1
        assert res.json()[0]["message"] == "Other user scam"

    def test_get_my_reports_empty_list(self, client, user_headers):
        res = client.get("/scam/my-reports", headers=user_headers)
        assert res.status_code == 200
        assert res.json() == []


class TestGetSingleReport:

    def test_get_own_report(self, client, user_headers, sample_report):
        res = client.get(f"/scam/{sample_report.id}", headers=user_headers)
        assert res.status_code == 200
        assert res.json()["id"] == sample_report.id

    def test_cannot_get_others_report(self, client, db, sample_report):
        from app.models.user import User
        from app.core.security import hash_password, create_access_token
        user2 = User(email="x@x.com", password=hash_password("p"), name="X")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        token2 = create_access_token({"user_id": user2.id, "role": "user"})

        res = client.get(f"/scam/{sample_report.id}",
            headers={"Authorization": f"Bearer {token2}"})
        assert res.status_code == 404

    def test_get_nonexistent_report(self, client, user_headers):
        res = client.get("/scam/99999", headers=user_headers)
        assert res.status_code == 404


class TestUpdateReport:

    def test_update_own_report(self, client, user_headers, sample_report):
        with patch("app.routes.scam.process_scam_report"):
            res = client.put(f"/scam/{sample_report.id}",
                json={"message": "Updated scam description"},
                headers=user_headers
            )
        assert res.status_code == 200
        assert res.json()["message"] == "Updated scam description"
        assert res.json()["status"] == "PENDING"

    def test_update_resets_to_pending(self, client, user_headers, verified_report):
        with patch("app.routes.scam.process_scam_report"):
            res = client.put(f"/scam/{verified_report.id}",
                json={"message": "New message"},
                headers=user_headers
            )
        assert res.json()["status"] == "PENDING"
        assert res.json()["prediction"] is None

    def test_cannot_update_others_report(self, client, db, sample_report):
        from app.models.user import User
        from app.core.security import hash_password, create_access_token
        user2 = User(email="x@x.com", password=hash_password("p"), name="X")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        token2 = create_access_token({"user_id": user2.id, "role": "user"})

        with patch("app.routes.scam.process_scam_report"):
            res = client.put(f"/scam/{sample_report.id}",
                json={"message": "hacked"},
                headers={"Authorization": f"Bearer {token2}"}
            )
        assert res.status_code == 404


class TestDeleteReport:

    def test_delete_own_report(self, client, user_headers, sample_report):
        res = client.delete(f"/scam/{sample_report.id}", headers=user_headers)
        assert res.status_code == 200
        assert "deleted" in res.json()["message"]

    def test_report_gone_after_delete(self, client, user_headers, sample_report, db):
        from app.models.scam_report import ScamReport
        client.delete(f"/scam/{sample_report.id}", headers=user_headers)
        assert db.query(ScamReport).filter(ScamReport.id == sample_report.id).first() is None

    def test_cannot_delete_others_report(self, client, db, sample_report):
        from app.models.user import User
        from app.core.security import hash_password, create_access_token
        user2 = User(email="x@x.com", password=hash_password("p"), name="X")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        token2 = create_access_token({"user_id": user2.id, "role": "user"})

        res = client.delete(f"/scam/{sample_report.id}",
            headers={"Authorization": f"Bearer {token2}"})
        assert res.status_code == 404

    def test_delete_nonexistent_report(self, client, user_headers):
        res = client.delete("/scam/99999", headers=user_headers)
        assert res.status_code == 404


class TestPublicSearch:

    def test_search_returns_verified_only(self, client, sample_report, verified_report):
        res = client.get("/scam/search/query?q=job")
        assert res.status_code == 200
        results = res.json()
        for r in results:
            assert r["status"] == "VERIFIED"

    def test_search_no_auth_needed(self, client, verified_report):
        res = client.get("/scam/search/query?q=scam")
        assert res.status_code == 200