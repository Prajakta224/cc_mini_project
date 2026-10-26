"""Audit service — helper to log security and operation events."""
import json
import secrets
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session
from app.models.audit_event import AuditEvent


def log_event(
    db: Session,
    event_type: str,
    success: bool,
    user_id: Optional[int] = None,
    ip_address: Optional[str] = None,
    details: Optional[dict] = None,
    correlation_id: Optional[str] = None,
) -> AuditEvent:
    """
    Persist an audit event.
    NEVER include passwords, plaintext keys, tokens, or file contents in details.
    """
    # Sanitise details dict — remove any potentially sensitive keys
    _FORBIDDEN_KEYS = {"password", "token", "key", "secret", "plaintext", "dek", "kek"}
    safe_details = {}
    if details:
        for k, v in details.items():
            if k.lower() not in _FORBIDDEN_KEYS:
                safe_details[k] = v

    event = AuditEvent(
        user_id=user_id,
        event_type=event_type,
        timestamp=datetime.now(timezone.utc),
        success=success,
        ip_address=ip_address,
        correlation_id=correlation_id or secrets.token_hex(8),
        details=json.dumps(safe_details) if safe_details else None,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
