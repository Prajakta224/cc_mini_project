"""Audit log router."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.audit_event import AuditEvent
from app.models.user import User
from app.schemas.audit import AuditListResponse, AuditEventResponse
from app.utils.security import get_current_user, require_admin

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("", response_model=AuditListResponse)
def get_audit_events(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    event_type: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Regular users see only their own audit events.
    Admins see all events.
    """
    query = db.query(AuditEvent)
    if current_user.role != "admin":
        query = query.filter(AuditEvent.user_id == current_user.id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type.upper())

    total = query.count()
    events = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return AuditListResponse(events=events, total=total)
