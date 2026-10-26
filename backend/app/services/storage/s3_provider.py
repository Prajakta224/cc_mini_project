"""
S3-compatible storage provider — works with both AWS S3 and MinIO.

IMPORTANT:
  When STORAGE_PROVIDER=minio, this connects to a local MinIO instance.
  MinIO is an S3-compatible open-source object storage server for local/demo use.
  It is NOT AWS S3. The UI clearly indicates which provider is active.

  When STORAGE_PROVIDER=s3, this connects to AWS S3 using IAM credentials.
  Objects are stored privately; no public access is granted.
"""
import io
import boto3
import botocore.exceptions
from typing import Optional
from app.services.storage.base import StorageProvider
from app.config import settings


class S3CompatibleProvider(StorageProvider):
    """
    Implements StorageProvider for both AWS S3 and MinIO via boto3.
    The S3-compatible API is identical; only endpoint and credentials differ.
    """

    def __init__(self):
        self._client = None
        self._bucket = None
        self._is_minio = settings.STORAGE_PROVIDER.lower() == "minio"
        self._setup()

    def _setup(self):
        """Initialize boto3 client based on configured provider."""
        if self._is_minio:
            protocol = "https" if settings.MINIO_SECURE else "http"
            self._client = boto3.client(
                "s3",
                endpoint_url=f"{protocol}://{settings.MINIO_ENDPOINT}",
                aws_access_key_id=settings.MINIO_ACCESS_KEY,
                aws_secret_access_key=settings.MINIO_SECRET_KEY,
                region_name="us-east-1",  # MinIO ignores region
            )
            self._bucket = settings.MINIO_BUCKET
        else:
            # AWS S3
            kwargs = {
                "region_name": settings.AWS_REGION,
            }
            if settings.AWS_ACCESS_KEY_ID:
                kwargs["aws_access_key_id"] = settings.AWS_ACCESS_KEY_ID
                kwargs["aws_secret_access_key"] = settings.AWS_SECRET_ACCESS_KEY
            self._client = boto3.client("s3", **kwargs)
            self._bucket = settings.S3_BUCKET

    def _ensure_bucket_exists(self):
        """Create bucket if it doesn't exist (MinIO dev mode)."""
        try:
            self._client.head_bucket(Bucket=self._bucket)
        except botocore.exceptions.ClientError as e:
            code = e.response["Error"]["Code"]
            if code in ("404", "NoSuchBucket"):
                try:
                    if self._is_minio or settings.AWS_REGION == "us-east-1":
                        self._client.create_bucket(Bucket=self._bucket)
                    else:
                        self._client.create_bucket(
                            Bucket=self._bucket,
                            CreateBucketConfiguration={"LocationConstraint": settings.AWS_REGION},
                        )
                    # Block all public access
                    self._client.put_public_access_block(
                        Bucket=self._bucket,
                        PublicAccessBlockConfiguration={
                            "BlockPublicAcls": True,
                            "IgnorePublicAcls": True,
                            "BlockPublicPolicy": True,
                            "RestrictPublicBuckets": True,
                        },
                    )
                except Exception:
                    pass  # MinIO may not support put_public_access_block

    def upload_object(self, key: str, data: bytes, content_type: str = "application/octet-stream") -> int:
        self._ensure_bucket_exists()
        extra_args = {"ContentType": content_type}
        # For AWS S3, add server-side encryption
        if not self._is_minio:
            extra_args["ServerSideEncryption"] = "AES256"
        self._client.put_object(
            Bucket=self._bucket,
            Key=key,
            Body=data,
            ContentType=content_type,
        )
        return len(data)

    def download_object(self, key: str) -> bytes:
        try:
            response = self._client.get_object(Bucket=self._bucket, Key=key)
            return response["Body"].read()
        except botocore.exceptions.ClientError as e:
            raise FileNotFoundError(f"Object '{key}' not found in storage: {e}")

    def delete_object(self, key: str) -> None:
        try:
            self._client.delete_object(Bucket=self._bucket, Key=key)
        except botocore.exceptions.ClientError as e:
            raise RuntimeError(f"Failed to delete object '{key}': {e}")

    def object_exists(self, key: str) -> bool:
        try:
            self._client.head_object(Bucket=self._bucket, Key=key)
            return True
        except botocore.exceptions.ClientError:
            return False

    def get_object_size(self, key: str) -> Optional[int]:
        try:
            response = self._client.head_object(Bucket=self._bucket, Key=key)
            return response.get("ContentLength")
        except botocore.exceptions.ClientError:
            return None

    def list_objects(self) -> list[dict]:
        try:
            self._ensure_bucket_exists()
            paginator = self._client.get_paginator("list_objects_v2")
            objects = []
            for page in paginator.paginate(Bucket=self._bucket):
                for obj in page.get("Contents", []):
                    objects.append({"key": obj["Key"], "size": obj["Size"]})
            return objects
        except Exception:
            return []

    def health_check(self) -> dict:
        base = {
            "provider": self.provider_name,
            "bucket": self._bucket,
            "mode": "MinIO (local S3-compatible)" if self._is_minio else "AWS S3",
        }
        try:
            self._ensure_bucket_exists()
            objects = self.list_objects()
            total_bytes = sum(o.get("size", 0) for o in objects)
            return {
                **base,
                "connected": True,
                "object_count": len(objects),
                "total_bytes": total_bytes,
                "message": "Storage connected and operational",
            }
        except Exception as e:
            return {
                **base,
                "connected": False,
                "object_count": 0,
                "total_bytes": 0,
                "message": f"Storage connection failed: {str(e)}",
            }

    @property
    def provider_name(self) -> str:
        return "MinIO" if self._is_minio else "AWS S3"
