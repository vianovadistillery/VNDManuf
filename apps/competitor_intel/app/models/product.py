from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .brand import Brand
    from .sku import SKU


PRODUCT_CATEGORIES = ("gin_bottle", "rtd_can")


class Product(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "products"

    brand_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    category: Mapped[str] = mapped_column(sa.String(32), nullable=False)
    abv_percent: Mapped[Decimal] = mapped_column(sa.Numeric(5, 2), nullable=False)
    notes: Mapped[str | None] = mapped_column(sa.Text())

    brand: Mapped["Brand"] = relationship("Brand", back_populates="products")
    skus: Mapped[list["SKU"]] = relationship(
        "SKU", back_populates="product", cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.UniqueConstraint("brand_id", "name", name="uq_products_brand_name"),
        sa.CheckConstraint(
            "category IN ('gin_bottle','rtd_can')",
            name="ck_products_category",
        ),
    )
