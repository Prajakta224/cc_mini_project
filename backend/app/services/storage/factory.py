"""Storage provider factory — selects provider based on configuration."""
from functools import lru_cache
from app.services.storage.base import StorageProvider
from app.config import settings


@lru_cache(maxsize=1)
def get_storage_provider() -> StorageProvider:
    """Return the configured storage provider (singleton)."""
    from app.services.storage.s3_provider import S3CompatibleProvider
    provider = settings.STORAGE_PROVIDER.lower()
    if provider in ("s3", "minio"):
        from app.services.storage.s3_provider import S3CompatibleProvider
        return S3CompatibleProvider()
    elif provider == "local":
        from app.services.storage.local_provider import LocalStorageProvider
        return LocalStorageProvider()
    raise ValueError(f"Unknown STORAGE_PROVIDER: '{provider}'. Use 's3', 'minio', or 'local'.")
