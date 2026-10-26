"""
Local Storage Provider — Offline simulated cloud object storage.
Used when Docker/MinIO is not installed locally, allowing full testing of
the encryption, decryption, and object management lifecycle offline.
Clearly labeled as "Local Storage Simulation" in UI and telemetry.
"""
import os
import shutil
from typing import Optional
from app.services.storage.base import StorageProvider

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "cloud_storage_simulation"))


class LocalStorageProvider(StorageProvider):
    """
    Offline local object storage simulation.
    Maps object keys to filesystem paths under cloud_storage_simulation/.
    Never masks itself as AWS S3 or MinIO.
    """

    def __init__(self):
        self._base_dir = STORAGE_DIR
        os.makedirs(self._base_dir, exist_ok=True)

    def _resolve_path(self, key: str) -> str:
        # Sanitize path to prevent directory traversal
        safe_key = key.replace("\\", "/").strip("/")
        full_path = os.path.abspath(os.path.join(self._base_dir, safe_key))
        if not full_path.startswith(self._base_dir):
            raise ValueError(f"Path traversal detected: {key}")
        return full_path

    def upload_object(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> int:
        target = self._resolve_path(key)
        os.makedirs(os.path.dirname(target), exist_ok=True)
        with open(target, "wb") as f:
            f.write(data)
        return len(data)

    def download_object(self, key: str) -> bytes:
        target = self._resolve_path(key)
        if not os.path.exists(target):
            raise FileNotFoundError(f"Object '{key}' not found in local simulation storage")
        with open(target, "rb") as f:
            return f.read()

    def delete_object(self, key: str) -> None:
        target = self._resolve_path(key)
        if os.path.exists(target):
            os.remove(target)
        else:
            raise FileNotFoundError(f"Object '{key}' not found for deletion")

    def object_exists(self, key: str) -> bool:
        target = self._resolve_path(key)
        return os.path.exists(target)

    def get_object_size(self, key: str) -> Optional[int]:
        target = self._resolve_path(key)
        if os.path.exists(target):
            return os.path.getsize(target)
        return None

    def list_objects(self) -> list[dict]:
        results = []
        for root, _, files in os.walk(self._base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                rel_key = os.path.relpath(full_path, self._base_dir).replace("\\", "/")
                results.append({
                    "key": rel_key,
                    "size": os.path.getsize(full_path),
                })
        return results

    def health_check(self) -> dict:
        objects = self.list_objects()
        total_bytes = sum(o["size"] for o in objects)
        return {
            "provider": self.provider_name,
            "connected": True,
            "bucket": "local-simulation-volume",
            "mode": "Local Filesystem Simulation (Offline)",
            "object_count": len(objects),
            "total_bytes": total_bytes,
            "message": "Local simulation storage operational (directory: cloud_storage_simulation)",
        }

    @property
    def provider_name(self) -> str:
        return "Local Simulation"
