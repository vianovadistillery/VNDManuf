from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .pack_spec import PackSpec
    from .package_spec import PackageSpec
    from .sku_carton import SKUCarton


class CartonSpec(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "carton_specs"

    units_per_carton: Mapped[int] = mapped_column(sa.Integer, nullable=False)
    pack_count: Mapped[int | None] = mapped_column(sa.Integer)
    package_spec_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("package_specs.id", ondelete="RESTRICT")
    )
    pack_spec_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("pack_specs.id", ondelete="RESTRICT")
    )
    gtin: Mapped[str | None] = mapped_column(sa.String(32), unique=True)
    notes: Mapped[str | None] = mapped_column(sa.Text())

    sku_links: Mapped[list["SKUCarton"]] = relationship(
        "SKUCarton", back_populates="carton_spec", cascade="all, delete-orphan"
    )
    package_spec: Mapped[Optional["PackageSpec"]] = relationship(
        "PackageSpec", back_populates="carton_specs"
    )
    pack_spec: Mapped[Optional["PackSpec"]] = relationship(
        "PackSpec", back_populates="carton_links"
    )

    __table_args__ = (
        sa.CheckConstraint(
            "(pack_spec_id IS NOT NULL AND package_spec_id IS NULL) OR (pack_spec_id IS NULL AND package_spec_id IS NOT NULL)",
            name="ck_carton_specs_pack_or_unit",
        ),
        sa.UniqueConstraint("gtin", name="uq_carton_specs_gtin"),
    )
