from __future__ import annotations

from typing import TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin, UUIDStringMixin

if TYPE_CHECKING:  # pragma: no cover
    from .product import Product


class Brand(UUIDStringMixin, TimestampMixin, Base):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    owner_company: Mapped[str | None] = mapped_column(sa.String(255))

    products: Mapped[list["Product"]] = relationship(
        "Product", back_populates="brand", cascade="all, delete-orphan"
    )

    __table_args__ = (
        sa.UniqueConstraint("name", name="uq_brands_name"),
        sa.Index("ix_brands_name", "name"),
    )
