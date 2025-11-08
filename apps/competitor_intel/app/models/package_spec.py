from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .carton_spec import CartonSpec
    from .pack_spec import PackSpec
    from .sku import SKU


PACKAGE_TYPES = ("bottle", "can")
CAN_FORM_FACTORS = ("slim", "sleek", "classic")


class PackageSpec(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "package_specs"

    type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    container_ml: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    can_form_factor: Mapped[str | None] = mapped_column(sa.String(32))

    skus: Mapped[list["SKU"]] = relationship(
        "SKU", back_populates="package_spec", cascade="all, delete-orphan"
    )
    pack_specs: Mapped[list["PackSpec"]] = relationship(
        "PackSpec", back_populates="package_spec", cascade="all, delete-orphan"
    )
    carton_specs: Mapped[list["CartonSpec"]] = relationship(
        "CartonSpec", back_populates="package_spec"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "type", "container_ml", "can_form_factor", name="uq_package_specs_unique"
        ),
        sa.CheckConstraint("type IN ('bottle','can')", name="ck_package_specs_type"),
        sa.CheckConstraint(
            "(type = 'can' AND can_form_factor IS NOT NULL) OR (type = 'bottle' AND can_form_factor IS NULL)",
            name="ck_package_specs_can_form_factor",
        ),
        sa.CheckConstraint(
            "(can_form_factor IS NULL) OR can_form_factor IN ('slim','sleek','classic')",
            name="ck_package_specs_can_form_factor_values",
        ),
    )
