"""Database mixins for soft delete, versioning, and archiving."""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String


class SoftDeleteMixin:
    """Mixin for soft delete functionality - marks records as deleted without removing them."""

    deleted_at = Column(DateTime, nullable=True, index=True)
    deleted_by = Column(String(100), nullable=True)


class VersioningMixin:
    """Mixin for record versioning - tracks changes with version numbers."""

    version = Column(Integer, nullable=False, default=1, index=True)
    versioned_at = Column(DateTime, nullable=True)
    versioned_by = Column(String(100), nullable=True)
    previous_version_id = Column(
        String(36), nullable=True
    )  # Reference to previous version


class ArchivingMixin:
    """Mixin for archiving functionality - marks records as archived."""

    archived_at = Column(DateTime, nullable=True, index=True)
    archived_by = Column(String(100), nullable=True)


class TimestampMixin:
    """Mixin for standard timestamp fields with UTC timezone."""

    created_at = Column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class AuditMixin(SoftDeleteMixin, VersioningMixin, ArchivingMixin, TimestampMixin):
    """Combined mixin for full audit trail: soft delete, versioning, archiving, and timestamps."""

    pass
