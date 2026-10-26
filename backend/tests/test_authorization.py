"""Tests for cross-user authorization — User A cannot access User B's files."""
import io
import pytest


def _upload_file(client, headers, content=b"Test content", filename="test.txt"):
    """Helper to upload and encrypt a file."""
    resp = client.post(
        "/api/files/encrypt",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        headers=headers,
    )
    return resp


class TestCrossUserAuthorization:
    def test_user_cannot_read_other_user_file(self, client, auth_headers, second_user):
        # User A uploads a file
        up = _upload_file(client, auth_headers)
        assert up.status_code == 201
        file_id = up.json()["file_id"]

        # User B attempts to read it
        b_headers = {"Authorization": f"Bearer {second_user['token']}"}
        resp = client.get(f"/api/files/{file_id}", headers=b_headers)
        assert resp.status_code == 403

    def test_user_cannot_decrypt_other_user_file(self, client, auth_headers, second_user):
        up = _upload_file(client, auth_headers)
        assert up.status_code == 201
        file_id = up.json()["file_id"]

        b_headers = {"Authorization": f"Bearer {second_user['token']}"}
        resp = client.post(f"/api/files/{file_id}/decrypt", headers=b_headers)
        assert resp.status_code == 403

    def test_user_cannot_delete_other_user_file(self, client, auth_headers, second_user):
        up = _upload_file(client, auth_headers)
        assert up.status_code == 201
        file_id = up.json()["file_id"]

        b_headers = {"Authorization": f"Bearer {second_user['token']}"}
        resp = client.delete(f"/api/files/{file_id}", headers=b_headers)
        assert resp.status_code == 403

    def test_unauthorized_access_creates_audit_event(self, client, auth_headers, second_user):
        up = _upload_file(client, auth_headers)
        file_id = up.json()["file_id"]

        b_headers = {"Authorization": f"Bearer {second_user['token']}"}
        client.get(f"/api/files/{file_id}", headers=b_headers)

        # Check audit log shows UNAUTHORIZED_ACCESS
        audit_resp = client.get("/api/audit", headers=b_headers)
        events = audit_resp.json()["events"]
        types = [e["event_type"] for e in events]
        assert "UNAUTHORIZED_ACCESS" in types

    def test_unauthenticated_request_rejected(self, client):
        resp = client.get("/api/files")
        assert resp.status_code == 403

    def test_user_sees_only_own_files(self, client, auth_headers, second_user):
        # User A uploads
        _upload_file(client, auth_headers, b"User A file")
        # User B uploads
        b_headers = {"Authorization": f"Bearer {second_user['token']}"}
        _upload_file(client, b_headers, b"User B file")

        a_files = client.get("/api/files", headers=auth_headers).json()["files"]
        b_files = client.get("/api/files", headers=b_headers).json()["files"]

        a_owners = set(f["id"] for f in a_files)
        b_owners = set(f["id"] for f in b_files)
        # No file IDs should overlap
        assert a_owners.isdisjoint(b_owners)
