"""
Abstract storage interface — defines the contract for all cloud storage providers.
"""
from abc import ABC, abstractmethod
from typing import Optional
import io


class StorageProvider(ABC):
    """Abstract base class for cloud object storage providers."""

    @abstractmethod
    def upload_object(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> int:
        """Upload bytes. Returns object size in bytes."""
        ...

    @abstractmethod
    def download_object(self, key: str) -> bytes:
        """Download and return object bytes. Raises if not found."""
        ...

    @abstractmethod
    def delete_object(self, key: str) -> None:
        """Delete an object. Raises if not found."""
        ...

    @abstractmethod
    def object_exists(self, key: str) -> bool:
        """Return True if the object exists."""
        ...

    @abstractmethod
    def get_object_size(self, key: str) -> Optional[int]:
        """Return object size in bytes, or None if not found."""
        ...

    @abstractmethod
    def list_objects(self) -> list[dict]:
        """Return list of objects with key and size."""
        ...

    @abstractmethod
    def health_check(self) -> dict:
        """Return dict with provider, connected (bool), message, bucket, object_count, total_bytes."""
        ...

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider name."""
        ...
