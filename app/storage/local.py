"""Local filesystem storage for CRM attachments."""

from __future__ import annotations

from pathlib import Path

from app.storage.base import StorageBackend, StoredFile

_DEFAULT_ROOT = Path(__file__).resolve().parents[2] / "uploads" / "crm"


class LocalStorageBackend(StorageBackend):
    def __init__(self, root: Path | None = None):
        self.root = root or _DEFAULT_ROOT
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, key: str) -> Path:
        full = self.root / key
        full.parent.mkdir(parents=True, exist_ok=True)
        return full

    def save(
        self, key: str, data: bytes, content_type: str | None = None
    ) -> StoredFile:
        path = self._path(key)
        path.write_bytes(data)
        return StoredFile(
            storage_backend="local",
            storage_key=key,
            file_name=path.name,
            mime_type=content_type,
            file_size=len(data),
        )

    def read(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        path = self._path(key)
        if path.exists():
            path.unlink()

    def url(self, key: str, expires_seconds: int = 3600) -> str | None:
        return None


def get_storage_backend() -> StorageBackend:
    return LocalStorageBackend()
