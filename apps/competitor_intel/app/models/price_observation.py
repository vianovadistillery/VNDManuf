from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .attachment import Attachment
    from .company import Company
    from .location import Location
    from .sku import SKU


CHANNELS = (
    "distributor_to_retailer",
    "wholesale_to_venue",
    "retail_instore",
    "retail_online",
    "direct_to_consumer",
)
PRICE_CONTEXTS = ("shelf", "promo", "member", "online", "quote", "other")
AVAILABILITY = ("in_stock", "low_stock", "out_of_stock", "unknown")
SOURCE_TYPES = ("web", "in_store", "brochure", "email", "verbal", "receipt", "photo")


class PriceObservation(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "price_observations"

    sku_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("skus.id", ondelete="CASCADE"), nullable=False
    )
    company_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("companies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    location_id: Mapped[str | None] = mapped_column(
        sa.String(36), sa.ForeignKey("locations.id", ondelete="SET NULL")
    )

    channel: Mapped[str] = mapped_column(sa.String(64), nullable=False)
    price_context: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, default="shelf"
    )
    promo_name: Mapped[str | None] = mapped_column(sa.String(255))
    availability: Mapped[str] = mapped_column(
        sa.String(32), nullable=False, default="unknown"
    )

    price_ex_gst_raw: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    price_inc_gst_raw: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    gst_rate: Mapped[Decimal] = mapped_column(
        sa.Numeric(6, 4), nullable=False, default=Decimal("0.10")
    )
    currency: Mapped[str] = mapped_column(sa.String(8), nullable=False, default="AUD")
    is_carton_price: Mapped[bool] = mapped_column(
        sa.Boolean, nullable=False, default=False
    )
    carton_units: Mapped[int | None] = mapped_column(sa.Integer)

    price_ex_gst_norm: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2), nullable=False
    )
    price_inc_gst_norm: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 2), nullable=False
    )
    unit_price_inc_gst: Mapped[Decimal] = mapped_column(
        sa.Numeric(12, 4), nullable=False
    )
    carton_price_inc_gst: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    pack_price_inc_gst: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 2))
    price_basis: Mapped[str] = mapped_column(
        sa.String(16), nullable=False, default="unit"
    )
    price_per_litre: Mapped[Decimal] = mapped_column(sa.Numeric(12, 4), nullable=False)
    price_per_unit_pure_alcohol: Mapped[Decimal] = mapped_column(
        sa.Numeric(14, 4), nullable=False
    )
    standard_drinks: Mapped[Decimal] = mapped_column(sa.Numeric(12, 4), nullable=False)

    observation_dt: Mapped[sa.DateTime] = mapped_column(
        sa.DateTime(timezone=True), nullable=False
    )
    source_type: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    source_url: Mapped[str | None] = mapped_column(sa.String(1024))
    source_note: Mapped[str | None] = mapped_column(sa.Text())

    hash_key: Mapped[str] = mapped_column(sa.String(128), nullable=False)

    gp_unit_abs: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    gp_unit_pct: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 4))
    gp_pack_abs: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    gp_pack_pct: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 4))
    gp_carton_abs: Mapped[Decimal | None] = mapped_column(sa.Numeric(12, 4))
    gp_carton_pct: Mapped[Decimal | None] = mapped_column(sa.Numeric(10, 4))

    sku: Mapped["SKU"] = relationship("SKU", back_populates="price_observations")
    company: Mapped["Company"] = relationship(
        "Company", back_populates="price_observations"
    )
    location: Mapped[Optional["Location"]] = relationship(
        "Location", back_populates="price_observations"
    )
    attachments: Mapped[list["Attachment"]] = relationship(
        "Attachment", back_populates="price_observation", cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.Index(
            "ix_price_observations_sku_id_observation_dt", "sku_id", "observation_dt"
        ),
        sa.Index(
            "ix_price_observations_company_id_observation_dt",
            "company_id",
            "observation_dt",
        ),
        sa.Index(
            "ix_price_observations_location_id_observation_dt",
            "location_id",
            "observation_dt",
        ),
        sa.Index(
            "ix_price_observations_channel_observation_dt", "channel", "observation_dt"
        ),
        sa.Index("ix_price_observations_observation_dt", "observation_dt"),
        sa.Index("ix_price_observations_hash_key", "hash_key"),
        sa.CheckConstraint(
            "channel IN ('distributor_to_retailer','wholesale_to_venue','retail_instore','retail_online','direct_to_consumer')",
            name="ck_price_observations_channel",
        ),
        sa.CheckConstraint(
            "price_context IN ('shelf','promo','member','online','quote','other')",
            name="ck_price_observations_price_context",
        ),
        sa.CheckConstraint(
            "availability IN ('in_stock','low_stock','out_of_stock','unknown')",
            name="ck_price_observations_availability",
        ),
        sa.CheckConstraint(
            "source_type IN ('web','in_store','brochure','email','verbal','receipt','photo')",
            name="ck_price_observations_source_type",
        ),
        sa.CheckConstraint(
            "price_basis IN ('unit','pack','carton')",
            name="ck_price_observations_basis",
        ),
    )
