from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator
from typing import List
import secrets


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # App
    APP_NAME: str = "AFES - Authenticated File Encryption System"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: str = secrets.token_hex(32)  # fallback for dev, must be set in prod
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "sqlite:///./afes.db"

    # Envelope encryption – Key Encryption Key (32 bytes as 64 hex chars)
    MASTER_KEK: str = ""

    # Storage
    STORAGE_PROVIDER: str = "minio"  # "minio" | "s3"

    # MinIO
    MINIO_ENDPOINT: str = "localhost:9000"
    MINIO_ACCESS_KEY: str = "minioadmin"
    MINIO_SECRET_KEY: str = "minioadmin123"
    MINIO_BUCKET: str = "afes-encrypted-files"
    MINIO_SECURE: bool = False

    # AWS S3
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    S3_BUCKET: str = ""

    # Upload limits
    MAX_UPLOAD_SIZE_MB: int = 100

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.CORS_ORIGINS.split(",") if o.strip()]

    @property
    def max_upload_bytes(self) -> int:
        return self.MAX_UPLOAD_SIZE_MB * 1024 * 1024

    def get_kek_bytes(self) -> bytes:
        """Return the 32-byte Key Encryption Key from hex env var."""
        if not self.MASTER_KEK or len(self.MASTER_KEK) != 64:
            raise ValueError(
                "MASTER_KEK must be a 64-character hex string (32 bytes). "
                "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
            )
        return bytes.fromhex(self.MASTER_KEK)


settings = Settings()
