from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .pack_spec import PackSpec
    from .sku import SKU


class SKUPack(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "sku_packs"

    sku_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False
    )
    pack_spec_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("pack_specs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    notes: Mapped[str | None] = mapped_column(sa.Text())

    sku: Mapped["SKU"] = relationship("SKU", back_populates="pack_assignment")
    pack_spec: Mapped["PackSpec"] = relationship("PackSpec", back_populates="sku_links")

    __table_args__ = (sa.UniqueConstraint("sku_id", name="uq_sku_packs_sku"),)


__all__ = ["SKUPack"]
