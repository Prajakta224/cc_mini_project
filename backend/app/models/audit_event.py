from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    # Types: REGISTER, LOGIN_SUCCESS, LOGIN_FAILURE, LOGOUT, ENCRYPT_FILE,
    #        DECRYPT_FILE, DELETE_FILE, UNAUTHORIZED_ACCESS, DOWNLOAD,
    #        STORAGE_ERROR, API_ERROR
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)
    success = Column(Boolean, nullable=False)
    ip_address = Column(String(50), nullable=True)
    correlation_id = Column(String(64), nullable=True)
    details = Column(Text, nullable=True)  # JSON string of safe non-sensitive metadata

    user = relationship("User", back_populates="audit_events")
