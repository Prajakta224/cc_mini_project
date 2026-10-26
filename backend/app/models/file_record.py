from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database import Base


class FileRecord(Base):
    __tablename__ = "file_records"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    # Original file info
    original_filename = Column(String(500), nullable=False)
    original_size = Column(BigInteger, nullable=False)
    content_type = Column(String(200), nullable=True)

    # Encryption info
    encrypted_object_key = Column(String(500), unique=True, nullable=False)  # S3/MinIO object key
    encrypted_size = Column(BigInteger, nullable=True)
    encryption_algorithm = Column(String(50), default="AES-256-GCM", nullable=False)
    format_version = Column(Integer, default=1, nullable=False)  # for future format changes
    nonce_hex = Column(String(64), nullable=False)               # 12-byte nonce as hex
    encrypted_dek_hex = Column(String(256), nullable=False)      # wrapped data key as hex

    # Storage info
    storage_provider = Column(String(20), nullable=False)  # "s3" | "minio"
    upload_timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active | deleted

    owner = relationship("User", back_populates="files")
