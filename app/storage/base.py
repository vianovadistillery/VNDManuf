"""Storage backend protocol for CRM attachments."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass
class StoredFile:
    storage_backend: str
    storage_key: str
    file_name: str
    mime_type: str | None = None
    file_size: int | None = None


class StorageBackend(Protocol):
    def save(
        self, key: str, data: bytes, content_type: str | None = None
    ) -> StoredFile: ...

    def read(self, key: str) -> bytes: ...

    def delete(self, key: str) -> None: ...

    def url(self, key: str, expires_seconds: int = 3600) -> str | None: ...
