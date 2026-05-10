"""
INTEGRATION TESTS — Admin routes
Tests: all admin endpoints, role-based access control
"""
import pytest


class TestAdminAccess:

    def test_regular_user_cannot_access_admin(self, client, user_headers):
        res = client.get("/admin/reports", headers=user_headers)
        assert res.status_code == 403

    def test_unauthenticated_cannot_access_admin(self, client):
        res = client.get("/admin/reports")
        assert res.status_code == 401

    def test_admin_can_access_admin_routes(self, client, admin_headers):
        res = client.get("/admin/reports", headers=admin_headers)
        assert res.status_code == 200


class TestAdminGetAllReports:

    def test_get_all_reports_empty(self, client, admin_headers):
        res = client.get("/admin/reports", headers=admin_headers)
        assert res.status_code == 200
        assert res.json() == []

    def test_get_all_reports_returns_all(self, client, admin_headers, sample_report, verified_report):
        res = client.get("/admin/reports", headers=admin_headers)
        assert len(res.json()) == 2

    def test_filter_by_status_pending(self, client, admin_headers, sample_report, verified_report):
        res = client.get("/admin/reports?status=PENDING", headers=admin_headers)
        results = res.json()
        assert all(r["status"] == "PENDING" for r in results)

    def test_filter_by_status_verified(self, client, admin_headers, sample_report, verified_report):
        res = client.get("/admin/reports?status=VERIFIED", headers=admin_headers)
        results = res.json()
        assert all(r["status"] == "VERIFIED" for r in results)

    def test_filter_by_scam_type(self, client, admin_headers, verified_report):
        res = client.get("/admin/reports?scam_type=JOB_SCAM", headers=admin_headers)
        results = res.json()
        assert len(results) == 1
        assert results[0]["scam_type"] == "JOB_SCAM"

    def test_pagination_limit(self, client, admin_headers, sample_report, verified_report):
        res = client.get("/admin/reports?limit=1", headers=admin_headers)
        assert len(res.json()) == 1

    def test_pagination_offset(self, client, admin_headers, sample_report, verified_report):
        res = client.get("/admin/reports?offset=1", headers=admin_headers)
        assert len(res.json()) == 1


class TestAdminGetSingleReport:

    def test_get_specific_report(self, client, admin_headers, sample_report):
        res = client.get(f"/admin/reports/{sample_report.id}", headers=admin_headers)
        assert res.status_code == 200
        assert res.json()["id"] == sample_report.id

    def test_get_nonexistent_report(self, client, admin_headers):
        res = client.get("/admin/reports/99999", headers=admin_headers)
        assert res.status_code == 404


class TestAdminDeleteReport:

    def test_admin_can_delete_any_report(self, client, admin_headers, sample_report):
        res = client.delete(f"/admin/reports/{sample_report.id}", headers=admin_headers)
        assert res.status_code == 200
        assert "deleted" in res.json()["message"]

    def test_report_gone_after_admin_delete(self, client, admin_headers, sample_report, db):
        from app.models.scam_report import ScamReport
        client.delete(f"/admin/reports/{sample_report.id}", headers=admin_headers)
        assert db.query(ScamReport).filter(ScamReport.id == sample_report.id).first() is None

    def test_delete_nonexistent_report(self, client, admin_headers):
        res = client.delete("/admin/reports/99999", headers=admin_headers)
        assert res.status_code == 404


class TestAdminVerifyReject:

    def test_admin_can_verify_report(self, client, admin_headers, sample_report, db):
        res = client.post(f"/admin/reports/{sample_report.id}/verify", headers=admin_headers)
        assert res.status_code == 200
        db.expire_all()
        db.refresh(sample_report)
        assert sample_report.status == "VERIFIED"

    def test_admin_can_reject_report(self, client, admin_headers, sample_report, db):
        res = client.post(f"/admin/reports/{sample_report.id}/reject", headers=admin_headers)
        assert res.status_code == 200
        db.expire_all()
        db.refresh(sample_report)
        assert sample_report.status == "REJECTED"

    def test_verify_nonexistent_report(self, client, admin_headers):
        res = client.post("/admin/reports/99999/verify", headers=admin_headers)
        assert res.status_code == 404


class TestAdminUsers:

    def test_get_all_users(self, client, admin_headers, regular_user, admin_user):
        res = client.get("/admin/users", headers=admin_headers)
        assert res.status_code == 200
        assert len(res.json()) == 2

    def test_deactivate_user(self, client, admin_headers, regular_user, db):
        res = client.post(f"/admin/users/{regular_user.id}/deactivate", headers=admin_headers)
        assert res.status_code == 200
        db.expire_all()
        db.refresh(regular_user)
        assert regular_user.is_active is False

    def test_deactivated_user_cannot_login(self, client, admin_headers, regular_user, db):
        client.post(f"/admin/users/{regular_user.id}/deactivate", headers=admin_headers)
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "password123"
        })
        assert res.status_code == 403