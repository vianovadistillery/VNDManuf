from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .sku import SKU


class ManufacturingCost(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "manufacturing_costs"

    sku_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False
    )
    cost_type: Mapped[str] = mapped_column(sa.String(16), nullable=False)
    cost_currency: Mapped[str] = mapped_column(
        sa.String(8), nullable=False, default="AUD"
    )
    cost_per_unit: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    cost_per_pack: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    cost_per_carton: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    effective_date: Mapped[date] = mapped_column(sa.Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())

    sku: Mapped["SKU"] = relationship("SKU", back_populates="manufacturing_costs")

    __table_args__ = (
        sa.CheckConstraint(
            "cost_type IN ('estimated','known')", name="ck_manufacturing_costs_type"
        ),
        sa.UniqueConstraint(
            "sku_id",
            "cost_type",
            "effective_date",
            name="uq_manufacturing_costs_sku_type_effective",
        ),
    )


__all__ = ["ManufacturingCost"]
