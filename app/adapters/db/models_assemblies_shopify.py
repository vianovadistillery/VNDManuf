import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

# Import the project Base and helper
from app.adapters.db.base import Base
from app.adapters.db.mixins import AuditMixin
from app.adapters.db.models import uuid_column


class AssemblyDirection(str, enum.Enum):
    MAKE_FROM_CHILDREN = "MAKE_FROM_CHILDREN"
    BREAK_INTO_CHILDREN = "BREAK_INTO_CHILDREN"


class Assembly(Base, AuditMixin):
    """Assembly header - defines how a parent product is assembled from components."""

    __tablename__ = "assemblies"

    id = uuid_column()
    parent_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    assembly_code = Column(String(50), nullable=False)
    assembly_name = Column(String(200), nullable=False)
    effective_from = Column(DateTime, nullable=True)
    effective_to = Column(DateTime, nullable=True)
    # Note: version, versioned_at, versioned_by, previous_version_id are provided by AuditMixin
    is_active = Column(Boolean, default=True)
    yield_factor = Column(Numeric(6, 4), default=1.0)
    is_primary = Column(Boolean, nullable=False, default=False)
    notes = Column(String(255), nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, archived_at, archived_by are provided by AuditMixin

    # Relationships
    parent_product = relationship("Product", foreign_keys=[parent_product_id])
    lines = relationship(
        "AssemblyLine", back_populates="assembly", cascade="all, delete-orphan"
    )

    __table_args__ = (Index("ix_assemblies_parent", "parent_product_id"),)


class AssemblyLine(Base, AuditMixin):
    """Assembly line item - defines component products and quantities."""

    __tablename__ = "assembly_lines"

    id = uuid_column()
    assembly_id = Column(String(36), ForeignKey("assemblies.id"), nullable=False)
    component_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity = Column(Numeric(12, 3), nullable=False)
    sequence = Column(Integer, nullable=False)
    unit = Column(String(10), nullable=True)
    is_energy_or_overhead = Column(Boolean, nullable=True)
    notes = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    assembly = relationship("Assembly", back_populates="lines")
    component_product = relationship("Product", foreign_keys=[component_product_id])

    __table_args__ = (
        UniqueConstraint("assembly_id", "sequence", name="uq_assembly_line_sequence"),
        Index("ix_assembly_line_assembly", "assembly_id"),
    )


class AssemblyCostDependency(Base):
    """Tracks cost dependencies between consumed and produced lots."""

    __tablename__ = "assembly_cost_dependencies"

    id = uuid_column()
    consumed_lot_id = Column(
        String(36), ForeignKey("inventory_lots.id"), nullable=False
    )
    produced_lot_id = Column(
        String(36), ForeignKey("inventory_lots.id"), nullable=False
    )
    consumed_txn_id = Column(
        String(36), ForeignKey("inventory_txns.id"), nullable=False
    )
    produced_txn_id = Column(
        String(36), ForeignKey("inventory_txns.id"), nullable=False
    )
    dependency_ts = Column(DateTime, nullable=False)

    # Relationships
    consumed_lot = relationship("InventoryLot", foreign_keys=[consumed_lot_id])
    produced_lot = relationship("InventoryLot", foreign_keys=[produced_lot_id])
    consumed_txn = relationship("InventoryTxn", foreign_keys=[consumed_txn_id])
    produced_txn = relationship("InventoryTxn", foreign_keys=[produced_txn_id])


class QualityTestDefinition(Base, AuditMixin):
    """Quality test definitions - reusable test templates."""

    __tablename__ = "quality_test_definitions"

    id = uuid_column()
    code = Column(String(50), nullable=False)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    test_type = Column(String(50), nullable=True)
    unit = Column(String(20), nullable=True)
    min_value = Column(Numeric(12, 3), nullable=True)
    max_value = Column(Numeric(12, 3), nullable=True)
    target_value = Column(Numeric(12, 3), nullable=True)
    is_active = Column(Boolean, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    __table_args__ = (Index("ix_quality_test_code", "code"),)


class Revaluation(Base, AuditMixin):
    """Inventory lot revaluations - tracks cost adjustments."""

    __tablename__ = "revaluations"

    id = uuid_column()
    item_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=True)
    old_unit_cost = Column(Numeric(10, 2), nullable=False)
    new_unit_cost = Column(Numeric(10, 2), nullable=False)
    delta_extended_cost = Column(Numeric(12, 2), nullable=False)
    reason = Column(Text, nullable=False)
    revalued_by = Column(String(100), nullable=False)
    revalued_at = Column(DateTime, nullable=False)
    propagated_to_assemblies = Column(Boolean, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    item = relationship("Product", foreign_keys=[item_id])
    lot = relationship("InventoryLot", foreign_keys=[lot_id])


class ProductMigrationMap(Base):
    """Maps legacy table records to unified product IDs."""

    __tablename__ = "product_migration_map"

    id = uuid_column()
    legacy_table = Column(String(50), nullable=False)
    legacy_id = Column(String(36), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    migrated_at = Column(DateTime, nullable=True)

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])

    __table_args__ = (
        UniqueConstraint("legacy_table", "legacy_id", name="uq_legacy_mapping"),
        Index("ix_migration_map_product", "product_id"),
    )


class ProductChannelLink(Base, AuditMixin):
    __tablename__ = "product_channel_links"
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    channel = Column(String(32), nullable=False, default="shopify")
    shopify_product_id = Column(String(64), nullable=True)
    shopify_variant_id = Column(String(64), nullable=True)
    shopify_location_id = Column(String(64), nullable=True)

    product = relationship("Product")
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin
    __table_args__ = (
        UniqueConstraint("product_id", "channel", name="uq_product_channel"),
    )


class InventoryReservation(Base, AuditMixin):
    __tablename__ = "inventory_reservations"
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    qty_canonical = Column(Numeric(18, 6), nullable=False)
    source = Column(String(16), nullable=False)  # 'shopify'|'internal'
    reference_id = Column(String(128), nullable=True)
    status = Column(
        String(16), nullable=False, default="ACTIVE"
    )  # ACTIVE|RELEASED|COMMITTED
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin
    product = relationship("Product")
