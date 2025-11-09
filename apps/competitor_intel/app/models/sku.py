from __future__ import annotations

from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .package_spec import PackageSpec
    from .price_observation import PriceObservation
    from .product import Product
    from .purchase_price import PurchasePrice
    from .sku_carton import SKUCarton
    from .sku_pack import SKUPack


class SKU(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "skus"

    product_id: Mapped[str] = mapped_column(
        sa.String(36), sa.ForeignKey("products.id", ondelete="RESTRICT"), nullable=False
    )
    package_spec_id: Mapped[str] = mapped_column(
        sa.String(36),
        sa.ForeignKey("package_specs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    gtin: Mapped[str | None] = mapped_column(sa.String(32), unique=True)
    is_active: Mapped[bool] = mapped_column(sa.Boolean, nullable=False, default=True)

    product: Mapped["Product"] = relationship("Product", back_populates="skus")
    package_spec: Mapped["PackageSpec"] = relationship(
        "PackageSpec", back_populates="skus"
    )
    carton_links: Mapped[list["SKUCarton"]] = relationship(
        "SKUCarton", back_populates="sku", cascade="all, delete-orphan"
    )
    price_observations: Mapped[list["PriceObservation"]] = relationship(
        "PriceObservation", back_populates="sku"
    )
    pack_assignment: Mapped[Optional["SKUPack"]] = relationship(
        "SKUPack", back_populates="sku", cascade="all, delete-orphan", uselist=False
    )
    purchase_prices: Mapped[list["PurchasePrice"]] = relationship(
        "PurchasePrice", back_populates="sku", cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.UniqueConstraint(
            "product_id", "package_spec_id", name="uq_skus_product_package"
        ),
    )
