"""Tests for AES-256-GCM encryption service."""
import pytest
import secrets
import os
os.environ.setdefault("MASTER_KEK", secrets.token_hex(32))
os.environ.setdefault("SECRET_KEY", secrets.token_hex(32))

from app.services.crypto_service import (
    encrypt_file, decrypt_file, tamper_test_envelope, FORMAT_VERSION, NONCE_SIZE
)


def test_encrypt_returns_valid_tuple():
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(b"Hello World", "test.txt", 1)
    assert isinstance(ciphertext, bytes)
    assert len(ciphertext) > len(b"Hello World")  # ciphertext + nonce + tag > plaintext
    assert len(bytes.fromhex(nonce_hex)) == NONCE_SIZE
    assert len(wrapped_dek_hex) > 0


def test_encrypt_decrypt_roundtrip():
    plaintext = b"Secret file content for AFES testing"
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(plaintext, "secret.txt", 42)
    recovered = decrypt_file(ciphertext, nonce_hex, wrapped_dek_hex, "secret.txt", 42)
    assert recovered == plaintext


def test_large_file_roundtrip():
    plaintext = secrets.token_bytes(5 * 1024 * 1024)  # 5 MB
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(plaintext, "large.bin", 1)
    recovered = decrypt_file(ciphertext, nonce_hex, wrapped_dek_hex, "large.bin", 1)
    assert recovered == plaintext


def test_tampered_ciphertext_rejected():
    plaintext = b"Sensitive data"
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(plaintext, "file.txt", 1)
    tampered = tamper_test_envelope(ciphertext)
    with pytest.raises(ValueError, match="authentication failed"):
        decrypt_file(tampered, nonce_hex, wrapped_dek_hex, "file.txt", 1)


def test_wrong_owner_rejected():
    """AAD includes owner_id — different owner should fail authentication."""
    plaintext = b"Owner-bound data"
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(plaintext, "file.txt", owner_id=1)
    with pytest.raises(ValueError):
        decrypt_file(ciphertext, nonce_hex, wrapped_dek_hex, "file.txt", owner_id=999)


def test_wrong_filename_rejected():
    """AAD includes filename — different filename should fail authentication."""
    plaintext = b"Filename-bound data"
    ciphertext, nonce_hex, wrapped_dek_hex = encrypt_file(plaintext, "original.txt", owner_id=1)
    with pytest.raises(ValueError):
        decrypt_file(ciphertext, nonce_hex, wrapped_dek_hex, "different.txt", owner_id=1)


def test_each_encryption_produces_unique_ciphertext():
    plaintext = b"Same content"
    ct1, nonce1, _ = encrypt_file(plaintext, "file.txt", 1)
    ct2, nonce2, _ = encrypt_file(plaintext, "file.txt", 1)
    # Different nonces must produce different ciphertexts
    assert nonce1 != nonce2
    assert ct1 != ct2


def test_wrapped_dek_is_not_plaintext_key():
    """Ensure stored wrapped DEK cannot be directly used as key."""
    _, _, wrapped_dek_hex = encrypt_file(b"data", "file.txt", 1)
    wrapped = bytes.fromhex(wrapped_dek_hex)
    # Wrapped DEK should be 60 bytes: 12 nonce + 32 DEK + 16 GCM tag
    assert len(wrapped) == 60
