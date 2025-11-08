from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .carton_spec import CartonSpec
    from .package_spec import PackageSpec
    from .sku_pack import SKUPack


class PackSpec(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "pack_specs"

    package_spec_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("package_specs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    units_per_pack: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    gtin: Mapped[str | None] = mapped_column(sa.String(32), unique=True)
    notes: Mapped[str | None] = mapped_column(sa.Text())

    package_spec: Mapped["PackageSpec"] = relationship(
        "PackageSpec", back_populates="pack_specs"
    )
    sku_links: Mapped[list["SKUPack"]] = relationship(
        "SKUPack", back_populates="pack_spec", cascade="all, delete-orphan"
    )
    carton_links: Mapped[list["CartonSpec"]] = relationship(
        "CartonSpec", back_populates="pack_spec"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "package_spec_id", "units_per_pack", name="uq_pack_specs_package_units"
        ),
    )


__all__ = ["PackSpec"]
