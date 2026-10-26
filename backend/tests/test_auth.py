"""Tests for authentication endpoints."""
import pytest


class TestRegister:
    def test_register_success(self, client):
        resp = client.post("/api/auth/register", json={
            "name": "Alice",
            "email": "alice@example.com",
            "password": "SecurePass1",
            "confirm_password": "SecurePass1",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert data["email"] == "alice@example.com"
        assert "password_hash" not in data
        assert "password" not in data

    def test_register_duplicate_email(self, client):
        payload = {"name": "Bob", "email": "bob@example.com",
                   "password": "SecurePass1", "confirm_password": "SecurePass1"}
        client.post("/api/auth/register", json=payload)
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 409

    def test_register_weak_password(self, client):
        resp = client.post("/api/auth/register", json={
            "name": "C", "email": "c@example.com",
            "password": "short", "confirm_password": "short",
        })
        assert resp.status_code == 422

    def test_register_password_mismatch(self, client):
        resp = client.post("/api/auth/register", json={
            "name": "D", "email": "d@example.com",
            "password": "SecurePass1", "confirm_password": "DifferentPass1",
        })
        assert resp.status_code == 422

    def test_register_no_plaintext_password_in_db(self, client):
        from tests.conftest import TestSessionLocal
        from app.models.user import User
        resp = client.post("/api/auth/register", json={
            "name": "User E", "email": "e@example.com",
            "password": "SecurePass1", "confirm_password": "SecurePass1",
        })
        assert resp.status_code == 201
        db = TestSessionLocal()
        user = db.query(User).filter(User.email == "e@example.com").first()
        db.close()
        assert user is not None
        assert user.password_hash != "SecurePass1"
        assert user.password_hash.startswith("$argon2id$")


class TestLogin:
    def test_login_success(self, client, registered_user):
        resp = client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": "Password123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client, registered_user):
        resp = client.post("/api/auth/login", json={
            "email": registered_user["email"],
            "password": "WrongPassword1",
        })
        assert resp.status_code == 401

    def test_login_unknown_email(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com",
            "password": "Password123",
        })
        assert resp.status_code == 401


class TestProtectedEndpoints:
    def test_me_without_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 403  # FastAPI HTTPBearer returns 403 when no credentials

    def test_me_with_token(self, client, auth_headers):
        resp = client.get("/api/auth/me", headers=auth_headers)
        assert resp.status_code == 200
        assert "email" in resp.json()
        assert "password_hash" not in resp.json()

    def test_me_invalid_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalidtoken"})
        assert resp.status_code == 401
