# Soft Delete, Versioning, and Archiving Implementation

This document describes the implementation of soft delete, versioning, and archiving functionality for all database tables.

## Overview

All database models now support:
1. **Soft Delete**: Records are marked as deleted with `deleted_at` timestamp instead of being removed
2. **Versioning**: Records track version numbers and version history
3. **Archiving**: Records can be archived with `archived_at` timestamp

## Architecture

### Mixins

All audit functionality is provided through mixin classes in `app/adapters/db/mixins.py`:

- `SoftDeleteMixin`: Adds `deleted_at` and `deleted_by` fields
- `VersioningMixin`: Adds `version`, `versioned_at`, `versioned_by`, and `previous_version_id` fields
- `ArchivingMixin`: Adds `archived_at` and `archived_by` fields
- `TimestampMixin`: Adds `created_at` and `updated_at` fields
- `AuditMixin`: Combined mixin that includes all of the above

### Models Updated

All models in `app/adapters/db/models.py` and `app/adapters/db/models_assemblies_shopify.py` now inherit from `AuditMixin`, providing:
- Soft delete functionality
- Version tracking
- Archiving capability
- Standard timestamps

### Service Functions

The `app/services/audit.py` module provides utility functions:

- `soft_delete(session, instance, deleted_by=None)`: Soft delete a record
- `restore_deleted(session, instance, restored_by=None)`: Restore a soft-deleted record
- `create_version(session, instance, versioned_by=None)`: Create a new version
- `archive_record(session, instance, archived_by=None)`: Archive a record
- `unarchive_record(session, instance, unarchived_by=None)`: Unarchive a record
- `filter_active(query, model_class)`: Filter out soft-deleted records
- `filter_non_archived(query, model_class)`: Filter out archived records
- `filter_active_and_non_archived(query, model_class)`: Filter out both deleted and archived records

## API Changes

All DELETE endpoints now perform soft delete instead of hard delete:

- `DELETE /api/products/{id}` - Soft deletes product
- `DELETE /api/formulas/{id}` - Soft deletes formula and its lines
- `DELETE /api/excise-rates/{id}` - Soft deletes excise rate
- `DELETE /api/units/{id}` - Soft deletes unit
- `DELETE /api/contacts/{id}` - Soft deletes contact
- `DELETE /api/suppliers/{id}` - Soft deletes supplier
- `DELETE /api/raw-materials/{id}` - Soft deletes raw material

## Database Schema

All tables now include these fields:

- `deleted_at` (DateTime, nullable): Timestamp when record was soft deleted
- `deleted_by` (String(100), nullable): User who performed the deletion
- `version` (Integer, default=1): Current version number
- `versioned_at` (DateTime, nullable): Timestamp when version was created
- `versioned_by` (String(100), nullable): User who created the version
- `previous_version_id` (String(36), nullable): Reference to previous version
- `archived_at` (DateTime, nullable): Timestamp when record was archived
- `archived_by` (String(100), nullable): User who performed the archiving
- `created_at` (DateTime, default=now): Timestamp when record was created
- `updated_at` (DateTime, default=now, onupdate=now): Timestamp when record was last updated

## Query Filtering

By default, queries should exclude soft-deleted records. Use the filter functions:

```python
from app.services.audit import filter_active

query = select(Product)
query = filter_active(query, Product)
products = db.execute(query).scalars().all()
```

Or manually filter:

```python
query = select(Product).where(Product.deleted_at.is_(None))
```

## Migration

An Alembic migration needs to be created to add these fields to existing tables. The migration should:

1. Add all new columns with nullable=True for existing records
2. Set default values where appropriate
3. Create indexes on `deleted_at` and `archived_at` for performance

## Usage Examples

### Soft Delete

```python
from app.services.audit import soft_delete

product = db.get(Product, product_id)
soft_delete(db, product, deleted_by="user123")
db.commit()
```

### Restore Deleted Record

```python
from app.services.audit import restore_deleted

product = db.get(Product, product_id)
restore_deleted(db, product, restored_by="user123")
db.commit()
```

### Archive Record

```python
from app.services.audit import archive_record

product = db.get(Product, product_id)
archive_record(db, product, archived_by="user123")
db.commit()
```

### Create Version

```python
from app.services.audit import create_version

formula = db.get(Formula, formula_id)
new_version = create_version(db, formula, versioned_by="user123")
db.commit()
```

## Notes

- Soft delete does not cascade to related records - they must be handled separately
- Versioning is incremental - each update can increment the version
- Archiving is separate from deletion - records can be archived without being deleted
- All timestamps use UTC timezone
- The `previous_version_id` field allows linking to previous versions for history tracking

## Future Enhancements

- Automatic version creation on update
- Archive tables for historical data
- Query scopes for common filtering patterns
- Audit log table for tracking all changes
