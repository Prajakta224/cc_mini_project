"""Tests for file encrypt/decrypt/delete API endpoints."""
import io
import pytest


def _upload(client, headers, content=b"Hello AFES!", filename="sample.txt"):
    return client.post(
        "/api/files/encrypt",
        files={"file": (filename, io.BytesIO(content), "text/plain")},
        headers=headers,
    )


class TestFileEncryption:
    def test_encrypt_success(self, client, auth_headers):
        resp = _upload(client, auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["original_filename"] == "sample.txt"
        assert data["encryption_algorithm"] == "AES-256-GCM"
        assert data["encrypted_size"] > data["original_size"]
        assert data["file_id"] > 0

    def test_encrypt_and_list(self, client, auth_headers):
        _upload(client, auth_headers, b"File 1", "f1.txt")
        _upload(client, auth_headers, b"File 2", "f2.txt")
        resp = client.get("/api/files", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["total"] >= 2

    def test_decrypt_roundtrip(self, client, auth_headers):
        original = b"Top secret document content for AFES demonstration"
        up = _upload(client, auth_headers, original, "secret.txt")
        assert up.status_code == 201
        file_id = up.json()["file_id"]

        dl = client.post(f"/api/files/{file_id}/decrypt", headers=auth_headers)
        assert dl.status_code == 200
        assert dl.content == original
        assert "attachment" in dl.headers.get("content-disposition", "")

    def test_tamper_test_detected(self, client, auth_headers):
        up = _upload(client, auth_headers, b"Tamper me", "tamper.txt")
        file_id = up.json()["file_id"]
        resp = client.post(f"/api/files/{file_id}/tamper-test", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["tamper_detected"] is True

    def test_delete_file(self, client, auth_headers):
        up = _upload(client, auth_headers, b"To be deleted", "delete_me.txt")
        file_id = up.json()["file_id"]
        del_resp = client.delete(f"/api/files/{file_id}", headers=auth_headers)
        assert del_resp.status_code == 204

        # File should no longer appear in list
        list_resp = client.get("/api/files", headers=auth_headers)
        ids = [f["id"] for f in list_resp.json()["files"]]
        assert file_id not in ids

    def test_empty_file_rejected(self, client, auth_headers):
        resp = client.post(
            "/api/files/encrypt",
            files={"file": ("empty.txt", io.BytesIO(b""), "text/plain")},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_stored_object_is_not_plaintext(self, client, auth_headers):
        """Verify the stored bytes are not the plaintext."""
        original = b"Plaintext that must not appear in storage"
        _upload(client, auth_headers, original, "check.txt")
        from tests.conftest import _mock_storage
        for stored in _mock_storage._store.values():
            assert original not in stored, "Plaintext found in storage — encryption not applied!"

    def test_metadata_persisted(self, client, auth_headers):
        up = _upload(client, auth_headers, b"Data", "meta.txt")
        file_id = up.json()["file_id"]
        resp = client.get(f"/api/files/{file_id}", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["original_filename"] == "meta.txt"
        assert data["encryption_algorithm"] == "AES-256-GCM"
        assert data["storage_provider"] == "MockStorage"
