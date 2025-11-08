from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column


def _naming_convention() -> Dict[str, str]:
    return {
        "ix": "ix_%(table_name)s_%(column_0_N_name)s",
        "uq": "uq_%(table_name)s_%(column_0_N_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
        "fk": "fk_%(table_name)s__%(column_0_name)s__%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
    }


def generate_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    metadata = sa.MetaData(naming_convention=_naming_convention())


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        sa.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        sa.DateTime(timezone=True), nullable=True
    )


class UUIDStringMixin:
    @declared_attr.directive
    def id(cls) -> Mapped[str]:  # type: ignore[override]
        return mapped_column(sa.String(36), primary_key=True, default=generate_uuid)


class SoftDeleteQueryMixin:
    __mapper_args__: Dict[str, Any] = {"eager_defaults": True}


__all__ = [
    "Base",
    "TimestampMixin",
    "UUIDStringMixin",
    "SoftDeleteQueryMixin",
    "generate_uuid",
]
