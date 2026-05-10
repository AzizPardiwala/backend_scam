import pytest
from unittest.mock import patch


class TestSubmitReport:

    def test_submit_report_success(self, client, user_headers):
        with patch("app.routes.submissions.process_submission"):
            res = client.post("/submissions/",
                json={"message": "Someone asked me to send money via UPI"},
                headers=user_headers
            )
        assert res.status_code == 202
        assert res.json()["status"] == "PENDING"
        assert res.json()["message"] == "Someone asked me to send money via UPI"
        assert "id" in res.json()

    def test_submit_report_no_auth(self, client):
        res = client.post("/submissions/", json={"message": "test scam"})
        assert res.status_code == 401

    def test_submit_report_empty_message(self, client, user_headers):
        res = client.post("/submissions/", json={}, headers=user_headers)
        assert res.status_code == 422

    def test_submit_report_creates_in_db(self, client, user_headers, db):
        from app.models.submission import ScamSubmission
        with patch("app.routes.submissions.process_submission"):
            client.post("/submissions/",
                json={"message": "Lottery fraud call"},
                headers=user_headers
            )
        sub = db.query(ScamSubmission).first()
        assert sub is not None
        assert sub.message == "Lottery fraud call"

    def test_submit_report_starts_as_pending(self, client, user_headers):
        with patch("app.routes.submissions.process_submission"):
            res = client.post("/submissions/",
                json={"message": "Fake job offer"},
                headers=user_headers
            )
        assert res.json()["status"] == "PENDING"


class TestGetMyReports:

    def test_get_my_reports_success(self, client, user_headers, sample_submission):
        res = client.get("/submissions/mine", headers=user_headers)
        assert res.status_code == 200
        assert isinstance(res.json(), list)
        assert len(res.json()) == 1

    def test_get_my_reports_no_auth(self, client):
        res = client.get("/submissions/mine")
        assert res.status_code == 401

    def test_get_my_reports_only_own(self, client, db, sample_submission):
        from app.models.user import User
        from app.models.submission import ScamSubmission
        from app.core.security import hash_password, create_access_token
        user2 = User(email="other@test.com", password=hash_password("pass"), name="Other")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        sub2 = ScamSubmission(user_id=user2.id, message="Other user scam", status="PENDING")
        db.add(sub2)
        db.commit()
        token2 = create_access_token({"user_id": user2.id, "role": "user"})
        res = client.get("/submissions/mine", headers={"Authorization": f"Bearer {token2}"})
        assert len(res.json()) == 1
        assert res.json()[0]["message"] == "Other user scam"

    def test_get_my_reports_empty_list(self, client, user_headers):
        res = client.get("/submissions/mine", headers=user_headers)
        assert res.status_code == 200
        assert res.json() == []


class TestGetSingleReport:

    def test_get_own_report(self, client, user_headers, sample_submission):
        res = client.get(f"/submissions/{sample_submission.id}", headers=user_headers)
        assert res.status_code == 200
        assert res.json()["id"] == sample_submission.id

    def test_cannot_get_others_report(self, client, db, sample_submission):
        from app.models.user import User
        from app.core.security import hash_password, create_access_token
        user2 = User(email="x@x.com", password=hash_password("p"), name="X")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        token2 = create_access_token({"user_id": user2.id, "role": "user"})
        res = client.get(f"/submissions/{sample_submission.id}",
            headers={"Authorization": f"Bearer {token2}"})
        assert res.status_code == 404

    def test_get_nonexistent_report(self, client, user_headers):
        res = client.get("/submissions/99999", headers=user_headers)
        assert res.status_code == 404


class TestUpdateReport:

    def test_update_own_report(self, client, user_headers, sample_submission):
        with patch("app.routes.submissions.process_submission"):
            res = client.put(f"/submissions/{sample_submission.id}",
                json={"message": "Updated scam description"},
                headers=user_headers
            )
        assert res.status_code == 200
        assert res.json()["message"] == "Updated scam description"
        assert res.json()["status"] == "PENDING"

    def test_cannot_update_others_report(self, client, db, sample_submission):
        from app.models.user import User
        from app.core.security import hash_password, create_access_token
        user2 = User(email="x@x.com", password=hash_password("p"), name="X")
        db.add(user2)
        db.commit()
        db.refresh(user2)
        token2 = create_access_token({"user_id": user2.id, "role": "user"})
        with patch("app.routes.submissions.process_submission"):
            res = client.put(f"/submissions/{sample_submission.id}",
                json={"message": "hacked"},
                headers={"Authorization": f"Bearer {token2}"}
            )
        assert res.status_code == 404


class TestDeleteReport:

    def test_delete_own_report(self, client, user_headers, sample_submission):
        res = client.delete(f"/submissions/{sample_submission.id}", headers=user_headers)
        assert res.status_code == 200
        assert "deleted" in res.json()["message"]

    def test_report_gone_after_delete(self, client, user_headers, sample_submission, db):
        from app.models.submission import ScamSubmission
        client.delete(f"/submissions/{sample_submission.id}", headers=user_headers)
        assert db.query(ScamSubmission).filter(
            ScamSubmission.id == sample_submission.id).first() is None

    def test_delete_nonexistent_report(self, client, user_headers):
        res = client.delete("/submissions/99999", headers=user_headers)
        assert res.status_code == 404


class TestPublicSearch:

    def test_search_no_auth_needed(self, client):
        res = client.get("/reports/")
        assert res.status_code == 200

    def test_search_returns_list(self, client):
        res = client.get("/reports/")
        assert isinstance(res.json(), list)