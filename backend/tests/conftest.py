"""
pytest conftest — shared fixtures for all tests.
Uses an in-memory SQLite DB and a test storage provider (no real S3/MinIO needed).
"""
import os
import secrets
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker
from unittest.mock import MagicMock, patch

# Set test env vars BEFORE importing app modules
os.environ.setdefault("MASTER_KEK", secrets.token_hex(32))
os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))
os.environ.setdefault("STORAGE_PROVIDER", "minio")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")

from app.database import Base, get_db
from app.main import app

# ── In-memory test database ──────────────────────────────────────────────────
TEST_DB_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DB_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Mock storage provider ────────────────────────────────────────────────────
class MockStorageProvider:
    def __init__(self):
        self._store: dict[str, bytes] = {}

    def upload_object(self, key, data, content_type="application/octet-stream"):
        self._store[key] = data
        return len(data)

    def download_object(self, key):
        if key not in self._store:
            raise FileNotFoundError(f"Object '{key}' not found")
        return self._store[key]

    def delete_object(self, key):
        self._store.pop(key, None)

    def object_exists(self, key):
        return key in self._store

    def get_object_size(self, key):
        return len(self._store[key]) if key in self._store else None

    def list_objects(self):
        return [{"key": k, "size": len(v)} for k, v in self._store.items()]

    def health_check(self):
        return {"provider": "MockStorage", "connected": True, "object_count": len(self._store),
                "total_bytes": sum(len(v) for v in self._store.values()),
                "bucket": "test-bucket", "message": "Mock storage operational"}

    @property
    def provider_name(self):
        return "MockStorage"


_mock_storage = MockStorageProvider()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield


@pytest.fixture(autouse=True)
def reset_storage():
    _mock_storage._store.clear()


@pytest.fixture
def client():
    app.dependency_overrides[get_db] = override_get_db
    with patch("app.services.storage.factory.get_storage_provider", return_value=_mock_storage):
        with patch("app.routers.files.get_storage_provider", return_value=_mock_storage):
            with patch("app.routers.cloud.get_storage_provider", return_value=_mock_storage):
                with TestClient(app) as c:
                    yield c
    app.dependency_overrides.clear()


@pytest.fixture
def registered_user(client):
    """Register and return a test user with token."""
    resp = client.post("/api/auth/register", json={
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "Password123",
        "confirm_password": "Password123",
    })
    assert resp.status_code == 201
    login = client.post("/api/auth/login", json={
        "email": "testuser@example.com",
        "password": "Password123",
    })
    token = login.json()["access_token"]
    return {"email": "testuser@example.com", "token": token}


@pytest.fixture
def auth_headers(registered_user):
    return {"Authorization": f"Bearer {registered_user['token']}"}


@pytest.fixture
def second_user(client):
    """Register a second test user."""
    resp = client.post("/api/auth/register", json={
        "name": "Second User",
        "email": "second@example.com",
        "password": "Password456",
        "confirm_password": "Password456",
    })
    assert resp.status_code == 201
    login = client.post("/api/auth/login", json={
        "email": "second@example.com",
        "password": "Password456",
    })
    token = login.json()["access_token"]
    return {"email": "second@example.com", "token": token}
