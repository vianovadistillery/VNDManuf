from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .company import Company
    from .price_observation import PriceObservation


class Location(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "locations"

    company_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id", ondelete="CASCADE"), nullable=False
    )
    store_name: Mapped[str | None] = mapped_column(sa.String(255))
    state: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    suburb: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    postcode: Mapped[str | None] = mapped_column(sa.String(16))
    lat: Mapped[float | None] = mapped_column(sa.Float)
    lon: Mapped[float | None] = mapped_column(sa.Float)

    company: Mapped["Company"] = relationship("Company", back_populates="locations")
    price_observations: Mapped[list["PriceObservation"]] = relationship(
        "PriceObservation", back_populates="location"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "company_id",
            "store_name",
            "state",
            "suburb",
            "postcode",
            name="uq_locations_company_store",
        ),
    )
