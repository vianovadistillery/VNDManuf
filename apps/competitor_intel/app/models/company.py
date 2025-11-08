from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .location import Location
    from .price_observation import PriceObservation


COMPANY_TYPES = ("distributor", "retailer", "venue", "other")


class Company(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    type: Mapped[str] = mapped_column(sa.String(32), nullable=False, default="other")
    parent_company_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("companies.id", ondelete="SET NULL")
    )

    parent_company: Mapped[Optional["Company"]] = relationship(
        "Company", remote_side="Company.id", back_populates="child_companies"
    )
    child_companies: Mapped[list["Company"]] = relationship(
        "Company", back_populates="parent_company"
    )
    locations: Mapped[list["Location"]] = relationship(
        "Location", back_populates="company", cascade="all, delete-orphan"
    )
    price_observations: Mapped[list["PriceObservation"]] = relationship(
        "PriceObservation", back_populates="company"
    )

    __table_args__ = (
        sa.UniqueConstraint("name", name="uq_companies_name"),
        sa.CheckConstraint(
            "type IN ('distributor','retailer','venue','other')",
            name="ck_companies_type",
        ),
    )
