from typing import Optional
from sqlalchemy import Column, String, Numeric, Enum, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship, Mapped, mapped_column
import enum
import datetime

# Import the project Base and helper
from app.adapters.db.base import Base
from app.adapters.db.models import Product, uuid_column

class AssemblyDirection(str, enum.Enum):
    MAKE_FROM_CHILDREN = "MAKE_FROM_CHILDREN"
    BREAK_INTO_CHILDREN = "BREAK_INTO_CHILDREN"

class Assembly(Base):
    __tablename__ = "assemblies"
    id = uuid_column()
    parent_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    child_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    ratio = Column(Numeric(18,6), nullable=False, default=1)
    direction = Column(String(32), nullable=False, default="MAKE_FROM_CHILDREN")
    loss_factor = Column(Numeric(6,4), nullable=False, default=0)

    parent_product = relationship("Product", foreign_keys=[parent_product_id])
    child_product = relationship("Product", foreign_keys=[child_product_id])

class ProductChannelLink(Base):
    __tablename__ = "product_channel_links"
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    channel = Column(String(32), nullable=False, default="shopify")
    shopify_product_id = Column(String(64), nullable=True)
    shopify_variant_id = Column(String(64), nullable=True)
    shopify_location_id = Column(String(64), nullable=True)

    product = relationship("Product")
    __table_args__ = (UniqueConstraint("product_id", "channel", name="uq_product_channel"),)

class InventoryReservation(Base):
    __tablename__ = "inventory_reservations"
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    qty_canonical = Column(Numeric(18,6), nullable=False)
    source = Column(String(16), nullable=False)  # 'shopify'|'internal'
    reference_id = Column(String(128), nullable=True)
    status = Column(String(16), nullable=False, default="ACTIVE")  # ACTIVE|RELEASED|COMMITTED
    created_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)
    product = relationship("Product")

