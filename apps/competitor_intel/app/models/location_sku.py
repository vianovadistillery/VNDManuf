from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .location import Location
    from .sku import SKU


class LocationSKU(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "location_skus"

    location_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sku_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("skus.id", ondelete="CASCADE"),
        nullable=False,
    )
    is_manual: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())
    first_observed_dt: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True)
    )
    last_observed_dt: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True)
    )

    location: Mapped["Location"] = relationship(
        "Location", back_populates="location_skus"
    )
    sku: Mapped["SKU"] = relationship("SKU", back_populates="location_links")

    __table_args__ = (
        sa.UniqueConstraint(
            "location_id",
            "sku_id",
            name="uq_location_skus_location_sku",
        ),
        sa.Index("ix_location_skus_location_id", "location_id"),
        sa.Index("ix_location_skus_sku_id", "sku_id"),
    )


__all__ = ["LocationSKU"]
