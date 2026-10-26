"""Files router — encrypt, list, download, delete."""
import secrets
import mimetypes
import os
import re
from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from fastapi.responses import Response, StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.file_record import FileRecord
from app.schemas.file import FileRecordResponse, FileListResponse, EncryptResponse
from app.services.crypto_service import encrypt_file, decrypt_file, tamper_test_envelope
from app.services.storage.factory import get_storage_provider
from app.services.audit_service import log_event
from app.utils.security import get_current_user
from app.config import settings
import io

router = APIRouter(prefix="/api/files", tags=["Files"])


def _safe_object_key(user_id: int, filename: str) -> str:
    """Generate a unique, safe S3 object key."""
    rand = secrets.token_hex(16)
    # Strip path separators and dangerous chars from filename
    safe = re.sub(r"[^\w.\-]", "_", os.path.basename(filename))[:100]
    return f"users/{user_id}/{rand}_{safe}.enc"


def _get_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/encrypt", response_model=EncryptResponse, status_code=status.HTTP_201_CREATED)
async def encrypt_upload(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Encrypt and upload a file to cloud storage."""
    # Validate file size
    contents = await file.read()
    if len(contents) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_MB} MB",
        )
    if len(contents) == 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")

    original_filename = file.filename or "unknown"
    content_type = file.content_type or mimetypes.guess_type(original_filename)[0] or "application/octet-stream"

    # Encrypt
    try:
        ciphertext, nonce_hex, encrypted_dek_hex = encrypt_file(
            contents, original_filename, current_user.id
        )
    except Exception as e:
        log_event(db, "ENCRYPT_FILE", False, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"filename": original_filename, "error": str(e)})
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"Encryption failed: {e}")

    # Upload to cloud storage
    object_key = _safe_object_key(current_user.id, original_filename)
    storage = get_storage_provider()
    try:
        enc_size = storage.upload_object(object_key, ciphertext, "application/octet-stream")
    except Exception as e:
        log_event(db, "ENCRYPT_FILE", False, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"filename": original_filename, "error": f"storage: {e}"})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Cloud storage upload failed: {e}")

    # Persist metadata
    record = FileRecord(
        owner_id=current_user.id,
        original_filename=original_filename,
        original_size=len(contents),
        content_type=content_type,
        encrypted_object_key=object_key,
        encrypted_size=len(ciphertext),
        encryption_algorithm="AES-256-GCM",
        format_version=1,
        nonce_hex=nonce_hex,
        encrypted_dek_hex=encrypted_dek_hex,
        storage_provider=storage.provider_name,
        upload_timestamp=datetime.now(timezone.utc),
        status="active",
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    log_event(db, "ENCRYPT_FILE", True, user_id=current_user.id,
              ip_address=_get_ip(request),
              details={
                  "file_id": record.id,
                  "filename": original_filename,
                  "original_size": len(contents),
                  "encrypted_size": len(ciphertext),
                  "object_key": object_key,
                  "provider": storage.provider_name,
              })

    return EncryptResponse(
        file_id=record.id,
        original_filename=original_filename,
        encrypted_object_key=object_key,
        encryption_algorithm="AES-256-GCM",
        original_size=len(contents),
        encrypted_size=len(ciphertext),
        storage_provider=storage.provider_name,
        upload_timestamp=record.upload_timestamp,
        message="File encrypted and uploaded successfully",
    )


@router.get("", response_model=FileListResponse)
def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all encrypted files owned by the current user."""
    files = (
        db.query(FileRecord)
        .filter(FileRecord.owner_id == current_user.id, FileRecord.status == "active")
        .order_by(FileRecord.upload_timestamp.desc())
        .all()
    )
    return FileListResponse(files=files, total=len(files))


@router.get("/{file_id}", response_model=FileRecordResponse)
def get_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get metadata for a single file. Enforces ownership."""
    record = _get_owned_record(file_id, current_user, db, request)
    return record


@router.post("/{file_id}/decrypt")
def decrypt_download(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Decrypt and download the original file. Enforces ownership + auth tag."""
    record = _get_owned_record(file_id, current_user, db, request)

    storage = get_storage_provider()
    # Download ciphertext from cloud storage
    try:
        ciphertext = storage.download_object(record.encrypted_object_key)
    except Exception as e:
        log_event(db, "DECRYPT_FILE", False, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"file_id": file_id, "error": f"storage download: {e}"})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Cloud storage download failed: {e}")

    # Decrypt and verify authentication tag
    try:
        plaintext = decrypt_file(
            ciphertext,
            record.nonce_hex,
            record.encrypted_dek_hex,
            record.original_filename,
            record.owner_id,
        )
    except ValueError as e:
        log_event(db, "DECRYPT_FILE", False, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"file_id": file_id, "error": "authentication_failed"})
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e))

    log_event(db, "DECRYPT_FILE", True, user_id=current_user.id,
              ip_address=_get_ip(request),
              details={"file_id": file_id, "filename": record.original_filename})

    content_type = record.content_type or "application/octet-stream"
    safe_fn = re.sub(r'[^\w.\-]', '_', record.original_filename)
    return Response(
        content=plaintext,
        media_type=content_type,
        headers={
            "Content-Disposition": f'attachment; filename="{safe_fn}"',
            "Content-Length": str(len(plaintext)),
        },
    )


@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_file(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a file from cloud storage and database."""
    record = _get_owned_record(file_id, current_user, db, request)

    storage = get_storage_provider()
    try:
        storage.delete_object(record.encrypted_object_key)
    except Exception as e:
        log_event(db, "DELETE_FILE", False, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"file_id": file_id, "error": str(e)})
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,
                            detail=f"Cloud storage deletion failed: {e}")

    record.status = "deleted"
    db.commit()

    log_event(db, "DELETE_FILE", True, user_id=current_user.id,
              ip_address=_get_ip(request),
              details={"file_id": file_id, "filename": record.original_filename})


@router.post("/{file_id}/tamper-test")
def tamper_test(
    file_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    DEVELOPMENT ONLY — demonstrate AES-GCM tamper detection.
    Downloads the ciphertext, flips a byte, attempts decryption, and shows it fails.
    Does NOT modify the stored object.
    """
    record = _get_owned_record(file_id, current_user, db, request)
    storage = get_storage_provider()
    try:
        ciphertext = storage.download_object(record.encrypted_object_key)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))

    tampered = tamper_test_envelope(ciphertext)
    try:
        decrypt_file(tampered, record.nonce_hex, record.encrypted_dek_hex,
                     record.original_filename, record.owner_id)
        # Should never reach here
        return {"tamper_detected": False, "message": "ERROR: tampering was NOT detected (unexpected)"}
    except ValueError:
        log_event(db, "TAMPER_TEST", True, user_id=current_user.id,
                  ip_address=_get_ip(request),
                  details={"file_id": file_id, "result": "tamper_detected_correctly"})
        return {
            "tamper_detected": True,
            "message": "AES-256-GCM authentication correctly detected ciphertext tampering. Decryption rejected.",
            "file_id": file_id,
        }


def _get_owned_record(file_id: int, user: User, db: Session, request: Request) -> FileRecord:
    """Return file record only if it belongs to the authenticated user."""
    record = db.query(FileRecord).filter(
        FileRecord.id == file_id, FileRecord.status == "active"
    ).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    if record.owner_id != user.id and user.role != "admin":
        # Log unauthorized access attempt
        log_event(
            db, "UNAUTHORIZED_ACCESS", False, user_id=user.id,
            ip_address=_get_ip(request),
            details={"attempted_file_id": file_id, "owner_id": record.owner_id},
        )
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    return record
