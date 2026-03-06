"""Pluggable file storage service.

Backends:
  local  — saves files to LOCAL_UPLOAD_PATH, served by FastAPI StaticFiles
  r2     — uploads to Cloudflare R2 (S3-compatible), returns public URL

Usage:
    from src.services.storage import get_storage
    storage = get_storage()
    url = await storage.upload(key, data, content_type)
"""

import asyncio
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from src.config import get_settings

# Allowed MIME types → file_type label
ALLOWED_TYPES: dict[str, str] = {
    "image/jpeg": "image",
    "image/jpg": "image",
    "image/png": "image",
    "image/gif": "image",
    "image/webp": "image",
    "image/svg+xml": "image",
    "application/pdf": "document",
    "application/msword": "document",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "document",
}

# Plan storage limits in bytes
PLAN_STORAGE_LIMITS: dict[str, int] = {
    "free": 50 * 1024 * 1024,       # 50 MB
    "pro": 500 * 1024 * 1024,       # 500 MB
    "agency": 5 * 1024 * 1024 * 1024,  # 5 GB
}

# Plan file count limits (0 = unlimited)
PLAN_FILE_LIMITS: dict[str, int] = {
    "free": 20,
    "pro": 0,
    "agency": 0,
}


def make_storage_key(site_id: str, original_filename: str) -> str:
    """Generate a unique, safe storage key for a file."""
    ext = Path(original_filename).suffix.lower()
    # Only keep safe extensions
    safe_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".pdf", ".doc", ".docx"}
    if ext not in safe_exts:
        ext = ""
    return f"{site_id}/{uuid.uuid4().hex}{ext}"


class StorageService(ABC):
    @abstractmethod
    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        """Upload file data and return the public URL."""
        ...

    @abstractmethod
    async def delete(self, key: str) -> None:
        """Delete a file from storage."""
        ...


class LocalStorageService(StorageService):
    """Stores files on the local filesystem. Served by FastAPI StaticFiles."""

    def __init__(self, upload_dir: str, base_url: str) -> None:
        self.upload_dir = Path(upload_dir)
        self.base_url = base_url.rstrip("/")

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        path = self.upload_dir / key
        path.parent.mkdir(parents=True, exist_ok=True)

        def _write() -> None:
            path.write_bytes(data)

        await asyncio.get_event_loop().run_in_executor(None, _write)
        return f"{self.base_url}/{key}"

    async def delete(self, key: str) -> None:
        path = self.upload_dir / key

        def _delete() -> None:
            if path.exists():
                path.unlink()

        await asyncio.get_event_loop().run_in_executor(None, _delete)


class R2StorageService(StorageService):
    """Uploads to Cloudflare R2 via S3-compatible API."""

    def __init__(
        self,
        account_id: str,
        access_key_id: str,
        secret_access_key: str,
        bucket_name: str,
        public_url: str,
    ) -> None:
        self.endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.bucket_name = bucket_name
        self.public_url = public_url.rstrip("/")

    def _get_client(self) -> Any:
        try:
            import boto3  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError(
                "boto3 is required for R2 storage. Install it: uv add boto3"
            ) from e
        return boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key_id,
            aws_secret_access_key=self.secret_access_key,
            region_name="auto",
        )

    async def upload(self, key: str, data: bytes, content_type: str) -> str:
        client = self._get_client()
        bucket = self.bucket_name

        def _put() -> None:
            client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
                CacheControl="public, max-age=31536000, immutable",
            )

        await asyncio.get_event_loop().run_in_executor(None, _put)
        return f"{self.public_url}/{key}"

    async def delete(self, key: str) -> None:
        client = self._get_client()
        bucket = self.bucket_name

        def _delete() -> None:
            client.delete_object(Bucket=bucket, Key=key)

        await asyncio.get_event_loop().run_in_executor(None, _delete)


def get_storage() -> StorageService:
    """Return the configured storage backend (cached per process)."""
    settings = get_settings()
    if settings.storage_backend == "r2":
        return R2StorageService(
            account_id=settings.r2_account_id,
            access_key_id=settings.r2_access_key_id,
            secret_access_key=settings.r2_secret_access_key,
            bucket_name=settings.r2_bucket_name,
            public_url=settings.r2_public_url,
        )
    return LocalStorageService(
        upload_dir=settings.local_upload_path,
        base_url=settings.upload_base_url,
    )
