"""Service functions for soft delete, versioning, and archiving."""

from datetime import datetime, timezone
from typing import Any, Optional, TypeVar

from sqlalchemy.orm import Session

from app.adapters.db.mixins import ArchivingMixin, SoftDeleteMixin, VersioningMixin

T = TypeVar("T")


def soft_delete(
    session: Session,
    instance: Any,
    deleted_by: Optional[str] = None,
) -> None:
    """
    Soft delete a record by setting deleted_at timestamp.

    Args:
        session: Database session
        instance: Model instance to soft delete
        deleted_by: User ID or username who performed the deletion
    """
    if not isinstance(instance, SoftDeleteMixin):
        raise ValueError(f"Instance {type(instance)} does not support soft delete")

    instance.deleted_at = datetime.now(timezone.utc)
    if deleted_by:
        instance.deleted_by = deleted_by
    # Note: Caller should commit the session


def restore_deleted(
    session: Session,
    instance: Any,
    restored_by: Optional[str] = None,
) -> None:
    """
    Restore a soft-deleted record.

    Args:
        session: Database session
        instance: Model instance to restore
        restored_by: User ID or username who performed the restoration
    """
    if not isinstance(instance, SoftDeleteMixin):
        raise ValueError(f"Instance {type(instance)} does not support soft delete")

    instance.deleted_at = None
    instance.deleted_by = None
    # Note: Caller should commit the session


def create_version(
    session: Session,
    instance: Any,
    versioned_by: Optional[str] = None,
) -> Any:
    """
    Create a new version of a record by incrementing version number.

    Args:
        session: Database session
        instance: Model instance to version
        versioned_by: User ID or username who created the version

    Returns:
        New instance with incremented version
    """
    if not isinstance(instance, VersioningMixin):
        raise ValueError(f"Instance {type(instance)} does not support versioning")

    # Get current version
    current_version = instance.version or 1

    # Create new versioned instance
    # This will be handled by the model's version tracking
    instance.version = current_version + 1
    instance.versioned_at = datetime.now(timezone.utc)
    if versioned_by:
        instance.versioned_by = versioned_by

    # Note: Caller should commit the session
    return instance


def archive_record(
    session: Session,
    instance: Any,
    archived_by: Optional[str] = None,
) -> None:
    """
    Archive a record by setting archived_at timestamp.

    Args:
        session: Database session
        instance: Model instance to archive
        archived_by: User ID or username who performed the archiving
    """
    if not isinstance(instance, ArchivingMixin):
        raise ValueError(f"Instance {type(instance)} does not support archiving")

    instance.archived_at = datetime.now(timezone.utc)
    if archived_by:
        instance.archived_by = archived_by

    # Also set is_archived flag if it exists
    if hasattr(instance, "is_archived"):
        instance.is_archived = True

    # Note: Caller should commit the session


def unarchive_record(
    session: Session,
    instance: Any,
    unarchived_by: Optional[str] = None,
) -> None:
    """
    Unarchive a record.

    Args:
        session: Database session
        instance: Model instance to unarchive
        unarchived_by: User ID or username who performed the unarchiving
    """
    if not isinstance(instance, ArchivingMixin):
        raise ValueError(f"Instance {type(instance)} does not support archiving")

    instance.archived_at = None
    instance.archived_by = None

    # Also clear is_archived flag if it exists
    if hasattr(instance, "is_archived"):
        instance.is_archived = False

    # Note: Caller should commit the session


def filter_active(query: Any, model_class: type) -> Any:
    """
    Filter query to exclude soft-deleted records.

    Args:
        query: SQLAlchemy query object
        model_class: Model class to check for soft delete support

    Returns:
        Filtered query
    """
    if issubclass(model_class, SoftDeleteMixin):
        return query.filter(model_class.deleted_at.is_(None))
    return query


def filter_non_archived(query: Any, model_class: type) -> Any:
    """
    Filter query to exclude archived records.

    Args:
        query: SQLAlchemy query object
        model_class: Model class to check for archiving support

    Returns:
        Filtered query
    """
    if issubclass(model_class, ArchivingMixin):
        return query.filter(model_class.archived_at.is_(None))
    return query


def filter_active_and_non_archived(query: Any, model_class: type) -> Any:
    """
    Filter query to exclude both soft-deleted and archived records.

    Args:
        query: SQLAlchemy query object
        model_class: Model class to check for soft delete and archiving support

    Returns:
        Filtered query
    """
    query = filter_active(query, model_class)
    query = filter_non_archived(query, model_class)
    return query
