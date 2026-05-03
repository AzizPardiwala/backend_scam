"""
INTEGRATION TESTS — Public Reports feed + User profile routes
"""
import pytest


class TestPublicReports:

    def test_public_feed_no_auth_needed(self, client):
        res = client.get("/reports/")
        assert res.status_code == 200

    def test_public_feed_returns_list(self, client):
        res = client.get("/reports/")
        assert isinstance(res.json(), list)

    def test_public_feed_only_verified(self, client, sample_report, verified_report):
        res = client.get("/reports/")
        results = res.json()
        for r in results:
            assert r["status"] == "VERIFIED"

    def test_pending_report_not_in_public_feed(self, client, sample_report):
        res = client.get("/reports/")
        ids = [r["id"] for r in res.json()]
        assert sample_report.id not in ids

    def test_verified_report_in_public_feed(self, client, verified_report):
        res = client.get("/reports/")
        ids = [r["id"] for r in res.json()]
        assert verified_report.id in ids

    def test_pagination_limit(self, client, verified_report):
        res = client.get("/reports/?limit=1")
        assert len(res.json()) <= 1


class TestUserProfile:

    def test_get_me(self, client, user_headers, regular_user):
        res = client.get("/user/me", headers=user_headers)
        assert res.status_code == 200
        assert res.json()["email"] == "user@test.com"
        assert res.json()["name"] == "Test User"

    def test_get_me_no_auth(self, client):
        res = client.get("/user/me")
        assert res.status_code == 401

    def test_update_name(self, client, user_headers):
        res = client.put("/user/update?name=NewName", headers=user_headers)
        assert res.status_code == 200

    def test_delete_account(self, client, user_headers, regular_user, db):
        res = client.delete("/user/delete", headers=user_headers)
        assert res.status_code == 200
        db.expire_all()
        db.refresh(regular_user)
        assert regular_user.is_active is False

    def test_deleted_user_cannot_login(self, client, user_headers):
        client.delete("/user/delete", headers=user_headers)
        res = client.post("/auth/login", json={
            "email": "user@test.com", "password": "password123"
        })
        assert res.status_code == 403


class TestHealthCheck:

    def test_health_ok(self, client):
        res = client.get("/health")
        assert res.status_code == 200
        assert res.json()["status"] == "ok"

    def test_root_ok(self, client):
        res = client.get("/")
        assert res.status_code == 200
        assert "version" in res.json()