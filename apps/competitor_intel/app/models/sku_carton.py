from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .carton_spec import CartonSpec
    from .sku import SKU


class SKUCarton(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "sku_cartons"

    sku_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False
    )
    carton_spec_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("carton_specs.id", ondelete="CASCADE"),
        nullable=False,
    )

    sku: Mapped["SKU"] = relationship("SKU", back_populates="carton_links")
    carton_spec: Mapped["CartonSpec"] = relationship(
        "CartonSpec", back_populates="sku_links"
    )

    __table_args__ = (
        sa.UniqueConstraint("sku_id", "carton_spec_id", name="uq_sku_cartons_parent"),
    )
