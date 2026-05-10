"""
INTEGRATION TESTS — Auth routes
"""
import pytest


class TestRegister:

    def test_register_success(self, client):
        res = client.post("/auth/register", json={
            "email": "new@test.com",
            "password": "pass123",
            "name": "New User"
        })
        assert res.status_code == 201
        data = res.json()
        assert "user_id" in data
        assert data["email"] == "new@test.com"

    def test_register_duplicate_email(self, client):
        payload = {"email": "dup@test.com", "password": "pass", "name": "A"}
        client.post("/auth/register", json=payload)
        res = client.post("/auth/register", json=payload)
        assert res.status_code == 400
        assert "already registered" in res.json()["detail"]

    def test_register_missing_email(self, client):
        res = client.post("/auth/register", json={"password": "pass", "name": "A"})
        assert res.status_code == 422

    def test_register_missing_password(self, client):
        res = client.post("/auth/register", json={"email": "x@x.com", "name": "A"})
        assert res.status_code == 422

    def test_register_missing_name(self, client):
        res = client.post("/auth/register", json={"email": "x@x.com", "password": "pass"})
        assert res.status_code == 422

    def test_register_returns_no_password(self, client):
        res = client.post("/auth/register", json={
            "email": "safe@test.com", "password": "secret", "name": "Safe"
        })
        assert "password" not in res.json()


class TestLogin:

    def test_login_success(self, client, regular_user):
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "password123"
        })
        assert res.status_code == 200
        data = res.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["role"] == "user"

    def test_login_returns_user_info(self, client, regular_user):
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "password123"
        })
        data = res.json()
        assert "user_id" in data
        assert "name" in data
        assert data["name"] == "Test User"

    def test_login_wrong_password(self, client, regular_user):
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "wrongpass"
        })
        assert res.status_code == 401

    def test_login_wrong_email(self, client):
        res = client.post("/auth/login", data={
            "username": "nobody@test.com",
            "password": "pass"
        })
        assert res.status_code == 401

    def test_login_deactivated_user(self, client, db, regular_user):
        regular_user.is_active = False
        db.commit()
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "password123"
        })
        assert res.status_code == 403

    def test_login_token_is_valid_jwt(self, client, regular_user):
        from jose import jwt
        from app.core.config import settings
        res = client.post("/auth/login", data={
            "username": "user@test.com",
            "password": "password123"
        })
        token = res.json()["access_token"]
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["user_id"] == regular_user.id

    def test_admin_login_returns_admin_role(self, client, admin_user):
        res = client.post("/auth/login", data={
            "username": "admin@test.com",
            "password": "adminpass"
        })
        assert res.json()["role"] == "admin"