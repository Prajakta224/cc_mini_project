"""
Crypto Service — AES-256-GCM authenticated encryption with envelope key management.

DESIGN:
  Envelope Encryption:
    1. A random 32-byte Data Encryption Key (DEK) is generated per file.
    2. The file is encrypted with AES-256-GCM using the DEK + a random 12-byte nonce.
    3. The DEK is wrapped (encrypted) with the Key Encryption Key (KEK) from env vars.
    4. The wrapped DEK is stored in the database alongside the nonce.
    5. The plaintext DEK is never stored anywhere.

  AWS KMS Extension Path:
    Replace _wrap_dek() / _unwrap_dek() with AWS KMS GenerateDataKey / Decrypt calls.
    The rest of the encryption/decryption logic remains unchanged.

WARNING:
  This uses a local master KEK derived from MASTER_KEK env var.
  This is suitable for DEVELOPMENT DEMONSTRATION ONLY.
  In production, replace with AWS KMS or another HSM-backed key management service.
"""
import os
import secrets
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from app.config import settings


# Format version – increment when changing the ciphertext envelope format
FORMAT_VERSION = 1
ALGORITHM_NAME = "AES-256-GCM"
NONCE_SIZE = 12   # bytes (96 bits, standard for GCM)
KEY_SIZE = 32     # bytes (256 bits)


def _get_kek() -> bytes:
    """Retrieve the Key Encryption Key from settings."""
    return settings.get_kek_bytes()


def _wrap_dek(dek: bytes) -> bytes:
    """
    Wrap (encrypt) the DEK using the KEK via AES-256-GCM.
    Returns: nonce (12 bytes) + ciphertext (32+16 bytes) = 60 bytes total.

    NOTE: In production, replace this with AWS KMS GenerateDataKey.
    """
    kek = _get_kek()
    nonce = secrets.token_bytes(NONCE_SIZE)
    aesgcm = AESGCM(kek)
    wrapped = nonce + aesgcm.encrypt(nonce, dek, b"AFES-DEK-WRAP-v1")
    return wrapped


def _unwrap_dek(wrapped_hex: str) -> bytes:
    """
    Unwrap (decrypt) the DEK using the KEK.

    NOTE: In production, replace this with AWS KMS Decrypt.
    """
    kek = _get_kek()
    wrapped = bytes.fromhex(wrapped_hex)
    nonce = wrapped[:NONCE_SIZE]
    ciphertext = wrapped[NONCE_SIZE:]
    aesgcm = AESGCM(kek)
    try:
        dek = aesgcm.decrypt(nonce, ciphertext, b"AFES-DEK-WRAP-v1")
    except Exception:
        raise ValueError("DEK unwrap failed: key may have changed or data is corrupted")
    return dek


def encrypt_file(
    plaintext: bytes,
    original_filename: str,
    owner_id: int,
) -> tuple[bytes, str, str]:
    """
    Encrypt file bytes using AES-256-GCM with a fresh random DEK.

    Additional authenticated data (AAD) binds the ciphertext to its metadata:
      "AFES:v1:<owner_id>:<safe_filename>"
    This prevents an attacker from re-using a ciphertext under a different owner
    or filename without breaking authentication.

    Returns:
        ciphertext (bytes): encrypted bytes (nonce prepended)
        nonce_hex (str): 12-byte nonce as hex
        encrypted_dek_hex (str): wrapped DEK as hex
    """
    dek = secrets.token_bytes(KEY_SIZE)
    nonce = secrets.token_bytes(NONCE_SIZE)
    aesgcm = AESGCM(dek)

    # Authenticated Additional Data — never changes for a given file
    safe_fn = _safe_filename_for_aad(original_filename)
    aad = f"AFES:v1:{owner_id}:{safe_fn}".encode()

    ciphertext = aesgcm.encrypt(nonce, plaintext, aad)

    # Prepend nonce to ciphertext for storage
    envelope = nonce + ciphertext

    # Wrap the DEK for storage
    wrapped_dek = _wrap_dek(dek)

    # Securely clear DEK from memory (best-effort in CPython)
    dek = b"\x00" * KEY_SIZE

    return envelope, nonce.hex(), wrapped_dek.hex()


def decrypt_file(
    envelope: bytes,
    nonce_hex: str,
    encrypted_dek_hex: str,
    original_filename: str,
    owner_id: int,
) -> bytes:
    """
    Decrypt a file encrypted by encrypt_file().
    Raises ValueError if authentication fails or key is wrong.
    Never returns unauthenticated data.
    """
    dek = _unwrap_dek(encrypted_dek_hex)
    nonce = bytes.fromhex(nonce_hex)

    # Strip prepended nonce from envelope
    ciphertext = envelope[NONCE_SIZE:]

    aesgcm = AESGCM(dek)
    safe_fn = _safe_filename_for_aad(original_filename)
    aad = f"AFES:v1:{owner_id}:{safe_fn}".encode()

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext, aad)
    except Exception:
        raise ValueError(
            "Decryption authentication failed. "
            "The file may have been tampered with, or the key configuration has changed."
        )
    finally:
        # Best-effort clear of DEK
        dek = b"\x00" * KEY_SIZE

    return plaintext


def _safe_filename_for_aad(filename: str) -> str:
    """Return a normalised filename safe to embed in AAD."""
    # Keep only ASCII printable chars, replace others with '_'
    return "".join(c if c.isascii() and c.isprintable() else "_" for c in filename)


def tamper_test_envelope(envelope: bytes) -> bytes:
    """
    Flip a byte in the ciphertext (after the nonce) to simulate tampering.
    Used ONLY in test endpoints — returns a broken envelope.
    """
    if len(envelope) <= NONCE_SIZE + 1:
        raise ValueError("Envelope too short to tamper with")
    ba = bytearray(envelope)
    # Flip a byte in the middle of the ciphertext
    mid = NONCE_SIZE + len(envelope) // 2
    ba[mid] ^= 0xFF
    return bytes(ba)
