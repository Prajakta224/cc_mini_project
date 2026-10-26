"""Cloud status and health router."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime, timezone
from app.database import get_db
from app.models.user import User
from app.models.file_record import FileRecord
from app.models.audit_event import AuditEvent
from app.services.storage.factory import get_storage_provider
from app.utils.security import get_current_user
from app.config import settings

router = APIRouter(tags=["Infrastructure"])


@router.get("/api/health")
def health_check(db: Session = Depends(get_db)):
    """API and database health check."""
    db_ok = True
    db_msg = "Database connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_ok = False
        db_msg = f"Database error: {e}"

    return {
        "status": "healthy" if db_ok else "degraded",
        "api": True,
        "database": db_ok,
        "database_message": db_msg,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": "1.0.0",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
    }


@router.get("/api/cloud/status")
def cloud_status(_: User = Depends(get_current_user)):
    """Return actual storage provider connection status."""
    storage = get_storage_provider()
    result = storage.health_check()
    result["warning"] = (
        "This is a LOCAL MinIO simulation, not AWS S3."
        if result.get("provider") == "MinIO"
        else None
    )
    return result


@router.post("/api/cloud/test")
def cloud_test(_: User = Depends(get_current_user)):
    """Run a live connectivity test (write + read + delete a probe object)."""
    import secrets as _s
    storage = get_storage_provider()
    probe_key = f"_health_probe/{_s.token_hex(8)}.txt"
    probe_data = b"AFES-health-probe"
    errors = []
    try:
        storage.upload_object(probe_key, probe_data, "text/plain")
    except Exception as e:
        errors.append(f"Write failed: {e}")

    if not errors:
        try:
            data = storage.download_object(probe_key)
            if data != probe_data:
                errors.append("Read returned unexpected data")
        except Exception as e:
            errors.append(f"Read failed: {e}")

    if not errors:
        try:
            storage.delete_object(probe_key)
        except Exception as e:
            errors.append(f"Delete failed: {e}")

    return {
        "provider": storage.provider_name,
        "test_passed": len(errors) == 0,
        "errors": errors,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@router.get("/api/cloud/stats")
def cloud_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Dashboard statistics from actual database records."""
    # Per-user stats
    user_files = (
        db.query(FileRecord)
        .filter(FileRecord.owner_id == current_user.id, FileRecord.status == "active")
        .all()
    )
    total_files = len(user_files)
    total_bytes = sum(f.original_size or 0 for f in user_files)
    encrypted_bytes = sum(f.encrypted_size or 0 for f in user_files)

    # Audit counts for current user
    from app.models.audit_event import AuditEvent
    encrypt_count = db.query(AuditEvent).filter(
        AuditEvent.user_id == current_user.id,
        AuditEvent.event_type == "ENCRYPT_FILE",
        AuditEvent.success == True,
    ).count()
    decrypt_ok = db.query(AuditEvent).filter(
        AuditEvent.user_id == current_user.id,
        AuditEvent.event_type == "DECRYPT_FILE",
        AuditEvent.success == True,
    ).count()
    decrypt_fail = db.query(AuditEvent).filter(
        AuditEvent.user_id == current_user.id,
        AuditEvent.event_type == "DECRYPT_FILE",
        AuditEvent.success == False,
    ).count()

    # Recent uploads (last 5)
    recent = sorted(user_files, key=lambda f: f.upload_timestamp, reverse=True)[:5]
    recent_list = [
        {
            "id": f.id,
            "filename": f.original_filename,
            "size": f.original_size,
            "uploaded": f.upload_timestamp.isoformat(),
        }
        for f in recent
    ]

    storage = get_storage_provider()

    return {
        "total_files": total_files,
        "total_original_bytes": total_bytes,
        "total_encrypted_bytes": encrypted_bytes,
        "encrypt_operations": encrypt_count,
        "successful_decryptions": decrypt_ok,
        "failed_decryptions": decrypt_fail,
        "recent_uploads": recent_list,
        "storage_provider": storage.provider_name,
    }
