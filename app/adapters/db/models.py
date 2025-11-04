# app/adapters/db/models.py
"""SQLAlchemy database models."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.settings import settings

from .base import Base
from .mixins import AuditMixin


class ContactType(str, enum.Enum):
    """Contact type classification."""

    CUSTOMER = "CUSTOMER"
    SUPPLIER = "SUPPLIER"
    OTHER = "OTHER"


def uuid_column(nullable: bool = False):
    """Return appropriate UUID column type based on database."""
    if settings.database.database_url.startswith("postgresql"):
        return Column(
            UUID(as_uuid=True), primary_key=True, nullable=nullable, default=uuid.uuid4
        )
    else:
        return Column(
            String(36),
            primary_key=True,
            nullable=nullable,
            default=lambda: str(uuid.uuid4()),
        )


# Core Product Models
class Product(Base, AuditMixin):
    __tablename__ = "products"

    # Primary Key - CRITICAL: Must be primary key and NOT NULL
    id = uuid_column(nullable=False)

    # Core Identification
    sku = Column(String(50), unique=True, nullable=True, index=True)
    name = Column(String(200), nullable=True)
    description = Column(Text)
    ean13 = Column(String(20))  # EAN-13 barcode

    # Product Type and Classification
    product_type = Column(String(20), nullable=True, index=True)  # RAW, WIP, FINISHED
    is_purchase = Column(Boolean, nullable=True, default=False)
    is_sell = Column(Boolean, nullable=True, default=False)
    is_assemble = Column(Boolean, nullable=True, default=False)
    is_tracked = Column(Boolean, nullable=True, default=False)
    sellable = Column(Boolean, nullable=True, default=False)
    is_archived = Column(Boolean, nullable=True, default=False)
    # Note: archived_at and archived_by are provided by AuditMixin

    # Raw Material Fields (RAW product type)
    raw_material_code = Column(Integer, nullable=True, index=True)
    # raw_material_group_id removed - deprecated
    raw_material_search_key = Column(String(10), nullable=True)
    raw_material_search_ext = Column(String(10), nullable=True)
    specific_gravity = Column(Numeric(10, 6), nullable=True)
    vol_solid = Column(Numeric(10, 6), nullable=True)
    solid_sg = Column(Numeric(10, 6), nullable=True)
    wt_solid = Column(Numeric(10, 6), nullable=True)
    usage_cost = Column(Numeric(10, 2), nullable=True)
    usage_unit = Column(String(10), nullable=True)
    usage_cost_ex_gst = Column(Numeric(10, 2), nullable=True)
    usage_cost_inc_gst = Column(Numeric(10, 2), nullable=True)
    usage_tax_included = Column(String(1), nullable=True)
    restock_level = Column(Numeric(12, 3), nullable=True)
    used_ytd = Column(Numeric(12, 3), nullable=True)
    hazard = Column(String(1), nullable=True)
    condition = Column(String(1), nullable=True)
    msds_flag = Column(String(1), nullable=True)
    altno1 = Column(Integer, nullable=True)
    altno2 = Column(Integer, nullable=True)
    altno3 = Column(Integer, nullable=True)
    altno4 = Column(Integer, nullable=True)
    altno5 = Column(Integer, nullable=True)
    last_movement_date = Column(String(10), nullable=True)
    last_purchase_date = Column(String(10), nullable=True)
    ean13_raw = Column(Numeric(18, 4), nullable=True)
    xero_account = Column(String(50), nullable=True)

    # Finished Goods Fields (FINISHED product type)
    # formula_id and formula_revision removed - deprecated (use Assembly section instead)

    # Physical Properties (moved to Basic Information in UI)
    size = Column(String(10))
    base_unit = Column(String(10))  # KG, LT, EA
    # pack and pkge removed - deprecated
    density_kg_per_l = Column(Numeric(10, 6))  # For L to kg conversions
    abv_percent = Column(Numeric(5, 2))  # ABV as % v/v

    # Purchase Information
    supplier_id = Column(
        String(36), ForeignKey("contacts.id"), nullable=True
    )  # Changed to contacts
    purchase_format_id = Column(
        String(36), ForeignKey("purchase_formats.id"), nullable=True
    )
    purchase_unit_id = Column(String(36), ForeignKey("units.id"), nullable=True)
    purchase_quantity = Column(
        Numeric(10, 3), nullable=True
    )  # Renamed from purchase_volume
    purchase_cost_ex_gst = Column(Numeric(10, 2), nullable=True)
    purchase_cost_inc_gst = Column(Numeric(10, 2), nullable=True)
    purchase_tax_included = Column(String(1), nullable=True)
    purchase_tax_included_bool = Column(Boolean, nullable=True)
    purcost = Column(Numeric(10, 2))  # Purchase cost (legacy)
    purtax = Column(Numeric(10, 2))  # Purchase tax (legacy)

    # Costing Information
    standard_cost = Column(Numeric(10, 2), nullable=True)
    estimated_cost = Column(Numeric(10, 2), nullable=True)
    estimate_reason = Column(Text, nullable=True)
    estimated_by = Column(String(100), nullable=True)
    estimated_at = Column(DateTime, nullable=True)
    manufactured_cost_ex_gst = Column(Numeric(10, 2), nullable=True)
    manufactured_cost_inc_gst = Column(Numeric(10, 2), nullable=True)
    manufactured_tax_included = Column(String(1), nullable=True)
    wholesalecost = Column(Numeric(10, 2))

    # Pricing - Retail
    retail_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    retail_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    retail_excise = Column(Numeric(10, 2), nullable=True)
    retailcde = Column(String(1))

    # Pricing - Wholesale
    wholesale_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    wholesale_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    wholesale_excise = Column(Numeric(10, 2), nullable=True)
    wholesalecde = Column(String(1))

    # Pricing - Counter
    counter_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    counter_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    counter_excise = Column(Numeric(10, 2), nullable=True)
    countercde = Column(String(1))

    # Pricing - Trade
    trade_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    trade_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    trade_excise = Column(Numeric(10, 2), nullable=True)
    tradecde = Column(String(1))

    # Pricing - Contract
    contract_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    contract_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    contract_excise = Column(Numeric(10, 2), nullable=True)
    contractcde = Column(String(1))

    # Pricing - Industrial
    industrial_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    industrial_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    industrial_excise = Column(Numeric(10, 2), nullable=True)
    industrialcde = Column(String(1))

    # Pricing - Distributor
    distributor_price_ex_gst = Column(Numeric(10, 2), nullable=True)
    distributor_price_inc_gst = Column(Numeric(10, 2), nullable=True)
    distributor_excise = Column(Numeric(10, 2), nullable=True)
    distributorcde = Column(String(1))

    # Product flags (from actual schema)
    dgflag = Column(String(1))  # Dangerous goods flag
    form = Column(String(10))  # Form code
    pkge = Column(Integer)  # Package type
    label = Column(Integer)  # Label type
    manu = Column(Integer)  # Manufacturer code

    # Financial/Tax
    taxinc = Column(String(1))  # Tax included flag
    salestaxcde = Column(String(1))  # Sales tax code

    # Discount Codes
    disccdeone = Column(String(1))  # Discount code 1
    disccdetwo = Column(String(1))  # Discount code 2

    # Xero Integration
    xero_item_id = Column(String(100))  # Xero Item UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero

    # Status and Timestamps
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    supplier = relationship("Contact", foreign_keys=[supplier_id])  # Changed to Contact
    purchase_format = relationship("PurchaseFormat", foreign_keys=[purchase_format_id])
    # raw_material_group relationship removed - field deprecated
    # formula relationship removed - fields deprecated
    variants = relationship("ProductVariant", back_populates="product")
    formulas = relationship(
        "Formula", back_populates="product", foreign_keys="Formula.product_id"
    )
    inventory_lots = relationship("InventoryLot", back_populates="product")
    pack_conversions = relationship("PackConversion", back_populates="product")
    price_list_items = relationship("PriceListItem", back_populates="product")
    customer_prices = relationship("CustomerPrice", back_populates="product")

    __table_args__ = (
        Index("ix_products_sku", "sku"),
        Index("ix_products_product_type", "product_type"),
        Index("ix_products_raw_material_code", "raw_material_code"),
        # Index for raw_material_group_id removed - field deprecated
        Index("ix_products_is_purchase", "is_purchase"),
        Index("ix_products_is_sell", "is_sell"),
        Index("ix_products_is_assemble", "is_assemble"),
    )


class ProductVariant(Base, AuditMixin):
    __tablename__ = "product_variants"

    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    variant_code = Column(String(50), nullable=False)
    variant_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    product = relationship("Product", back_populates="variants")

    __table_args__ = (
        UniqueConstraint("product_id", "variant_code", name="uq_product_variant_code"),
    )


# Formula Models
class Formula(Base, AuditMixin):
    __tablename__ = "formulas"

    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    formula_code = Column(String(50), nullable=False)
    formula_name = Column(String(200), nullable=False)
    # Note: version, versioned_at, versioned_by, previous_version_id are provided by AuditMixin
    is_active = Column(Boolean, default=True)
    is_archived = Column(Boolean, default=False, nullable=False)
    # Note: archived_at, archived_by are provided by AuditMixin
    notes = Column(Text, nullable=True)
    instructions = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by are provided by AuditMixin

    # Relationships
    product = relationship(
        "Product", foreign_keys=[product_id], back_populates="formulas"
    )
    lines = relationship("FormulaLine", back_populates="formula")

    __table_args__ = (
        UniqueConstraint(
            "product_id", "formula_code", "version", name="uq_formula_version"
        ),
    )


class FormulaLine(Base, AuditMixin):
    __tablename__ = "formula_lines"

    id = uuid_column()
    formula_id = Column(String(36), ForeignKey("formulas.id"), nullable=False)
    product_id = Column(
        String(36), ForeignKey("products.id"), nullable=True
    )  # Unified product reference (nullable per DB)
    quantity_kg = Column(Numeric(12, 3), nullable=False)  # Canonical storage in kg
    sequence = Column(Integer, nullable=False)
    notes = Column(Text)
    unit = Column(String(10))  # Display unit (kg, g, L, mL, etc.)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    formula = relationship("Formula", back_populates="lines")
    product = relationship("Product")

    # Backward compatibility properties for raw_material
    @property
    def raw_material(self):
        """Backward compatibility: return product for raw_material."""
        return self.product

    @raw_material.setter
    def raw_material(self, value):
        """Backward compatibility: set product from raw_material."""
        self.product = value

    @property
    def raw_material_id(self):
        """Backward compatibility: return product_id as raw_material_id."""
        return self.product_id

    @raw_material_id.setter
    def raw_material_id(self, value):
        """Backward compatibility: set product_id from raw_material_id."""
        self.product_id = value

    __table_args__ = (
        UniqueConstraint("formula_id", "sequence", name="uq_formula_line_sequence"),
    )


# Inventory Models
class InventoryLot(Base, AuditMixin):
    __tablename__ = "inventory_lots"

    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    lot_code = Column(String(50), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)  # Canonical storage in kg
    unit_cost = Column(Numeric(10, 2))  # Cost per kg (current)
    original_unit_cost = Column(Numeric(10, 2))  # Original cost at receipt
    current_unit_cost = Column(Numeric(10, 2))  # Current adjusted cost
    received_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    product = relationship("Product", back_populates="inventory_lots")
    transactions = relationship("InventoryTxn", back_populates="lot")

    __table_args__ = (
        UniqueConstraint("product_id", "lot_code", name="uq_lot_code"),
        Index("ix_lot_product_code", "product_id", "lot_code"),
    )


class InventoryTxn(Base, AuditMixin):
    __tablename__ = "inventory_txns"

    id = uuid_column()
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # RECEIPT, ISSUE, ADJUSTMENT
    quantity_kg = Column(
        Numeric(12, 3), nullable=False
    )  # Positive for receipts, negative for issues
    unit_cost = Column(Numeric(10, 2))
    extended_cost = Column(Numeric(12, 2))  # quantity * unit_cost
    cost_source = Column(String(20))  # ACTUAL, ESTIMATED, STANDARD
    estimate_flag = Column(Boolean, default=False)
    estimate_reason = Column(Text)
    reference_type = Column(String(50))  # PURCHASE_ORDER, WORK_ORDER, SALES_ORDER, etc.
    reference_id = Column(String(36))
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin
    created_by = Column(String(100))

    # Relationships
    lot = relationship("InventoryLot", back_populates="transactions")

    __table_args__ = (Index("ix_txn_lot_ts", "lot_id", "created_at"),)


# Work Order Models
class WorkOrder(Base, AuditMixin):
    __tablename__ = "work_orders"

    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    assembly_id = Column(
        String(36), ForeignKey("assemblies.id"), nullable=True
    )  # Primary recipe source
    formula_id = Column(
        String(36), ForeignKey("formulas.id"), nullable=True
    )  # Legacy, kept for backward compatibility
    quantity_kg = Column(
        Numeric(12, 3), nullable=False
    )  # Legacy field, use planned_qty
    planned_qty = Column(
        Numeric(12, 4), nullable=True
    )  # Planned quantity from run size
    uom = Column(String(10), nullable=True)  # Unit of measure (L, can, bottle, etc.)
    work_center = Column(String(50), nullable=True)  # e.g., Still01, Canning01
    status = Column(
        String(20), default="draft"
    )  # draft, released, in_progress, hold, complete, void
    start_time = Column(DateTime, nullable=True)  # Set on in_progress
    end_time = Column(DateTime, nullable=True)  # Set on complete
    batch_code = Column(
        String(50), unique=True, nullable=True, index=True
    )  # Generated batch code
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin
    released_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)

    # Relationships
    product = relationship("Product")
    assembly = relationship("Assembly", foreign_keys=[assembly_id])  # Primary recipe
    formula = relationship("Formula")  # Legacy
    lines = relationship("WorkOrderLine", back_populates="work_order")
    batches = relationship("Batch", back_populates="work_order")
    outputs = relationship("WorkOrderOutput", back_populates="work_order")
    qc_tests = relationship("WoQcTest", back_populates="work_order")
    timers = relationship("WoTimer", back_populates="work_order")

    __table_args__ = (
        Index("ix_work_order_code", "code"),
        Index("ix_work_order_status", "status"),
        Index("ix_work_order_product_status", "product_id", "status"),
        Index("ix_work_order_batch_code", "batch_code"),
    )


class WorkOrderLine(Base, AuditMixin):
    """Work order input line - tracks planned and actual material consumption."""

    __tablename__ = "work_order_lines"

    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    component_product_id = Column(
        String(36), ForeignKey("products.id"), nullable=False
    )  # Renamed from ingredient_product_id
    ingredient_product_id = Column(
        String(36), ForeignKey("products.id"), nullable=True
    )  # Legacy field for backward compatibility
    required_quantity_kg = Column(
        Numeric(12, 3), nullable=True
    )  # Legacy, use planned_qty
    allocated_quantity_kg = Column(Numeric(12, 3), default=0)  # Legacy, use actual_qty
    planned_qty = Column(Numeric(12, 4), nullable=True)  # From assembly explosion
    actual_qty = Column(Numeric(12, 4), nullable=True)  # Set on issue/close
    uom = Column(String(10), nullable=True)  # Unit of measure
    source_batch_id = Column(
        String(36), ForeignKey("batches.id"), nullable=True
    )  # If batch-tracked input
    unit_cost = Column(Numeric(12, 4), nullable=True)  # FIFO snapshot at issue
    line_type = Column(
        String(20), nullable=True, default="material"
    )  # 'material', 'overhead'
    sequence = Column(Integer, nullable=False)
    note = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    work_order = relationship("WorkOrder", back_populates="lines")
    component_product = relationship("Product", foreign_keys=[component_product_id])
    ingredient_product = relationship(
        "Product", foreign_keys=[ingredient_product_id]
    )  # Legacy
    source_batch = relationship("Batch", foreign_keys=[source_batch_id])

    __table_args__ = (Index("ix_work_order_line_wo_id", "work_order_id"),)


# Batch Models
class Batch(Base, AuditMixin):
    """Generalized batch model - can be work-order-specific or standalone."""

    __tablename__ = "batches"

    id = uuid_column()
    product_id = Column(
        String(36), ForeignKey("products.id"), nullable=True
    )  # For generalized batches
    work_order_id = Column(
        String(36), ForeignKey("work_orders.id"), nullable=True
    )  # Made nullable
    batch_code = Column(
        String(50), unique=True, nullable=False, index=True
    )  # Unique across all batches
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    mfg_date = Column(Date, nullable=True)  # Manufacturing date
    exp_date = Column(Date, nullable=True)  # Expiration date
    status = Column(
        String(20), default="open"
    )  # open, quarantined, released, closed (updated from DRAFT/IN_PROGRESS/COMPLETED)
    meta = Column(Text, nullable=True)  # JSON metadata (e.g., ABV, genealogy)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Extended status for new workflow (legacy)
    batch_status = Column(String(20), default="planned")  # planned, in_process, closed

    # Actual production results
    yield_actual = Column(Numeric(12, 3))  # Actual yield in kg
    yield_litres = Column(Numeric(12, 3))  # Actual yield in litres
    variance_percent = Column(Numeric(5, 2))  # Variance percentage

    # Relationships
    product = relationship("Product", foreign_keys=[product_id])
    work_order = relationship("WorkOrder", back_populates="batches")
    components = relationship("BatchComponent", back_populates="batch")
    qc_results = relationship("QcResult", back_populates="batch")
    batch_lines = relationship(
        "BatchLine", back_populates="batch", cascade="all, delete-orphan"
    )
    work_order_outputs = relationship("WorkOrderOutput", back_populates="batch")

    __table_args__ = (
        UniqueConstraint(
            "batch_code", name="uq_batch_code_unique"
        ),  # Global unique constraint
        Index("ix_batch_product_status", "product_id", "status"),
    )


class BatchComponent(Base, AuditMixin):
    __tablename__ = "batch_components"

    id = uuid_column()
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
    ingredient_product_id = Column(
        String(36), ForeignKey("products.id"), nullable=False
    )
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_cost = Column(Numeric(10, 2))
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    batch = relationship("Batch", back_populates="components")
    ingredient_product = relationship("Product", foreign_keys=[ingredient_product_id])
    lot = relationship("InventoryLot")


# Finished Goods Models
class FinishedGood(Base, AuditMixin):
    """Finished goods - sellable products."""

    __tablename__ = "finished_goods"

    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=False)
    base_unit = Column(String(10), nullable=False, default="LT")  # LT or KG
    formula_id = Column(
        String(36), ForeignKey("formulas.id")
    )  # Optional link to default formula
    formula_revision = Column(Integer)  # Formula revision
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    inventory = relationship(
        "FinishedGoodInventory", back_populates="finished_good", uselist=False
    )


class FinishedGoodInventory(Base):
    """Stock on hand for finished goods."""

    __tablename__ = "finished_goods_inventory"

    fg_id = Column(
        String(36),
        ForeignKey("finished_goods.id", ondelete="CASCADE"),
        primary_key=True,
    )
    soh = Column(Numeric(12, 3), nullable=False, default=0)

    # Relationships
    finished_good = relationship("FinishedGood", back_populates="inventory")


class BatchLine(Base, AuditMixin):
    """Snapshot of materials used in a batch."""

    __tablename__ = "batch_lines"

    id = uuid_column()
    batch_id = Column(
        String(36), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False
    )
    material_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    role = Column(String(50))  # resin/solvent/additive/etc
    qty_theoretical = Column(
        Numeric(12, 3), nullable=False
    )  # From formula scaled by yield
    qty_actual = Column(Numeric(12, 3))  # Entered/adjusted at execution
    unit = Column(String(10), nullable=False)  # KG/LT/EA
    cost_at_time = Column(Numeric(10, 2))  # Cost capture
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    batch = relationship("Batch")
    material = relationship("Product")

    __table_args__ = (
        UniqueConstraint("batch_id", "material_id", name="uq_batch_line"),
        Index("ix_batch_line_batch", "batch_id"),
    )


class InventoryMovement(Base, AuditMixin):
    """Single source of truth ledger for all stock changes - extended per spec."""

    __tablename__ = "inventory_movements"

    id = uuid_column()
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)  # UTC timestamp
    timestamp = Column(DateTime, nullable=True)  # Alias for ts, per spec
    date = Column(String(10), nullable=False)  # Business date (YYYY-MM-DD)
    product_id = Column(
        String(36), ForeignKey("products.id"), nullable=True
    )  # Unified product reference (nullable per DB)
    batch_id = Column(
        String(36), ForeignKey("batches.id"), nullable=True
    )  # Batch reference (per spec)
    qty = Column(Numeric(12, 4), nullable=False)  # Can be +in or -out (per spec)
    unit = Column(String(10), nullable=False)
    uom = Column(String(10), nullable=True)  # Alias for unit, per spec
    direction = Column(
        String(10), nullable=True
    )  # IN or OUT (legacy, can derive from qty sign)
    move_type = Column(
        String(50), nullable=True
    )  # wo_issue, wo_completion, receipt, etc.
    ref_table = Column(
        String(50), nullable=True
    )  # e.g., 'work_orders', 'purchase_orders'
    ref_id = Column(String(36), nullable=True)  # Reference ID (e.g., WO id)
    unit_cost = Column(Numeric(12, 4), nullable=True)  # Cost at time of move (per spec)
    source_batch_id = Column(
        String(36), ForeignKey("batches.id"), nullable=True
    )  # Legacy field
    note = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    product = relationship("Product")
    batch = relationship("Batch", foreign_keys=[batch_id])
    source_batch = relationship("Batch", foreign_keys=[source_batch_id])  # Legacy

    __table_args__ = (
        Index("ix_movements_product", "product_id"),
        Index("ix_movements_date", "date"),
        Index("ix_movements_batch", "batch_id"),
        Index("ix_movements_move_type", "move_type"),
        Index("ix_movements_ref", "ref_table", "ref_id"),
        Index("ix_movements_product_ts", "product_id", "timestamp"),
    )


class QcResult(Base, AuditMixin):
    __tablename__ = "qc_results"

    id = uuid_column()
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
    test_definition_id = Column(
        String(36), ForeignKey("quality_test_definitions.id"), nullable=True
    )
    test_name = Column(String(100), nullable=False)
    test_value = Column(Numeric(12, 3))
    test_unit = Column(String(20))
    pass_fail = Column(Boolean)
    tested_at = Column(DateTime, default=datetime.utcnow)
    tested_by = Column(String(100))
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    batch = relationship("Batch", back_populates="qc_results")
    test_definition = relationship(
        "QualityTestDefinition", foreign_keys=[test_definition_id]
    )


# Work Order Output Models
class WorkOrderOutput(Base, AuditMixin):
    """Work order output - tracks finished products produced."""

    __tablename__ = "work_order_outputs"

    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    product_id = Column(
        String(36), ForeignKey("products.id"), nullable=False
    )  # Usually same as WO.product_id
    qty_produced = Column(Numeric(12, 4), nullable=False)  # Actual finished qty
    uom = Column(String(10), nullable=False)
    batch_id = Column(
        String(36), ForeignKey("batches.id"), nullable=False
    )  # Newly created batch
    unit_cost = Column(Numeric(12, 4), nullable=True)  # Set at cost roll-up
    scrap_qty = Column(Numeric(12, 4), nullable=True)  # Optional
    note = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    work_order = relationship("WorkOrder", back_populates="outputs")
    product = relationship("Product")
    batch = relationship("Batch", back_populates="work_order_outputs")

    __table_args__ = (Index("ix_wo_output_wo_id", "work_order_id"),)


# Work Order QC Tests
class WoQcTest(Base, AuditMixin):
    """QC tests linked to work orders (separate from batch QC)."""

    __tablename__ = "wo_qc_tests"

    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    test_type = Column(String(50), nullable=False)  # 'ABV', 'fill', 'pH', etc.
    result_value = Column(Numeric(12, 4), nullable=True)  # Numeric result
    result_text = Column(Text, nullable=True)  # Text result (for non-numeric)
    unit = Column(String(20), nullable=True)  # %, pH, NTU, etc.
    status = Column(
        String(20), nullable=False, default="pending"
    )  # pending, pass, fail
    tested_at = Column(DateTime, nullable=True)
    tester = Column(String(100), nullable=True)
    note = Column(Text, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    work_order = relationship("WorkOrder", back_populates="qc_tests")

    __table_args__ = (Index("ix_wo_qc_test_wo_id", "work_order_id"),)


# Work Order Timers (telemetry costing)
class WoTimer(Base, AuditMixin):
    """Timer records for overhead costing (e.g., still runtime, canning hours)."""

    __tablename__ = "wo_timers"

    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    timer_type = Column(
        String(50), nullable=False
    )  # 'still_runtime', 'canning_hours', etc.
    seconds = Column(Integer, nullable=False)
    rate_per_hour = Column(Numeric(12, 4), nullable=True)  # Snapshot rate
    cost = Column(Numeric(12, 4), nullable=True)  # Derived: seconds/3600*rate
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    work_order = relationship("WorkOrder", back_populates="timers")


# Product Cost Rates (overheads library)
class ProductCostRate(Base, AuditMixin):
    """Cost rate definitions for overheads (canning, energy, labor, etc.)."""

    __tablename__ = "product_cost_rates"

    id = uuid_column()
    rate_code = Column(
        String(50), unique=True, nullable=False, index=True
    )  # e.g., CANNING_LINE_STD_HOURLY
    rate_type = Column(String(20), nullable=False)  # 'hourly', 'per_unit', 'fixed'
    rate_value = Column(Numeric(12, 4), nullable=False)
    uom = Column(String(20), nullable=True)  # e.g., AUD/hour
    effective_from = Column(DateTime, nullable=False)
    effective_to = Column(DateTime, nullable=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    __table_args__ = (Index("ix_cost_rate_code", "rate_code"),)


# Batch Sequence Table (for deterministic batch code generation)
class BatchSeq(Base):
    """Sequence table for deterministic batch code generation per product/date."""

    __tablename__ = "batch_seq"

    id = uuid_column()  # Primary key for ORM
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    date = Column(String(10), nullable=False)  # YYYYMMDD
    seq = Column(Integer, nullable=False, default=0)
    # Note: No AuditMixin - this is a pure sequence table

    __table_args__ = (
        UniqueConstraint("product_id", "date", name="uq_batch_seq_product_date"),
    )


# Unified Contact Models (Supersedes separate Supplier/Customer)
class Contact(Base, AuditMixin):
    """Unified contact model for customers, suppliers, and other contacts."""

    __tablename__ = "contacts"

    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)

    # Contact type flags (can be multiple)
    is_customer = Column(Boolean, default=False, nullable=False, index=True)
    is_supplier = Column(Boolean, default=False, nullable=False, index=True)
    is_other = Column(Boolean, default=False, nullable=False)

    # Additional fields
    tax_rate = Column(Numeric(5, 2), default=10.0)  # Default GST rate for customers
    xero_contact_id = Column(String(100))  # Xero Contact UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships - commented out until FK columns are added
    # purchase_orders = relationship("PurchaseOrder", back_populates="contact", foreign_keys="PurchaseOrder.contact_id")
    # sales_orders = relationship("SalesOrder", back_populates="contact", foreign_keys="SalesOrder.contact_id")
    # invoices = relationship("Invoice", back_populates="contact", foreign_keys="Invoice.contact_id")
    # customer_prices = relationship("CustomerPrice", back_populates="contact", foreign_keys="CustomerPrice.contact_id")

    __table_args__ = (
        Index("ix_contact_code", "code"),
        Index("ix_contact_type", "is_customer", "is_supplier", "is_other"),
    )

    @property
    def contact_types(self) -> list[str]:
        """Return list of active contact types."""
        types = []
        if self.is_customer:
            types.append("CUSTOMER")
        if self.is_supplier:
            types.append("SUPPLIER")
        if self.is_other:
            types.append("OTHER")
        return types


# Supplier and Purchase Order Models (DEPRECATED - use Contact instead)
class Supplier(Base, AuditMixin):
    __tablename__ = "suppliers"

    id = uuid_column()
    code = Column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        default=lambda: str(uuid.uuid4()),
    )
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    xero_contact_id = Column(String(100))  # Xero Contact UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")

    __table_args__ = (Index("ix_supplier_code", "code"),)


class PurchaseOrder(Base, AuditMixin):
    __tablename__ = "purchase_orders"

    id = uuid_column()
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default="DRAFT")  # DRAFT, SENT, RECEIVED, CANCELLED
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_date = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    lines = relationship("PoLine", back_populates="purchase_order")

    __table_args__ = (Index("ix_purchase_order_po_number", "po_number"),)


class PoLine(Base, AuditMixin):
    __tablename__ = "po_lines"

    id = uuid_column()
    purchase_order_id = Column(
        String(36), ForeignKey("purchase_orders.id"), nullable=False
    )
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    sequence = Column(Integer, nullable=False)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    product = relationship("Product")


# Customer and Sales Order Models
class Customer(Base, AuditMixin):
    __tablename__ = "customers"

    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    tax_rate = Column(Numeric(5, 2), default=10.0)  # Default GST rate
    xero_contact_id = Column(String(100))  # Xero Contact UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    sales_orders = relationship("SalesOrder", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    customer_prices = relationship("CustomerPrice", back_populates="customer")

    __table_args__ = (Index("ix_customer_code", "code"),)


class SalesOrder(Base, AuditMixin):
    __tablename__ = "sales_orders"

    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    so_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(
        String(20), default="DRAFT"
    )  # DRAFT, CONFIRMED, SHIPPED, INVOICED, CANCELLED
    order_date = Column(DateTime, default=datetime.utcnow)
    requested_date = Column(DateTime)
    shipped_date = Column(DateTime)
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    lines = relationship("SoLine", back_populates="sales_order")
    invoices = relationship("Invoice", back_populates="sales_order")

    __table_args__ = (Index("ix_sales_order_so_number", "so_number"),)


class SoLine(Base, AuditMixin):
    __tablename__ = "so_lines"

    id = uuid_column()
    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    line_total_ex_tax = Column(Numeric(12, 2), nullable=False)
    line_total_inc_tax = Column(Numeric(12, 2), nullable=False)
    sequence = Column(Integer, nullable=False)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    sales_order = relationship("SalesOrder", back_populates="lines")
    product = relationship("Product")


# Invoice Models
class Invoice(Base, AuditMixin):
    __tablename__ = "invoices"

    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"))
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    status = Column(
        String(20), default="DRAFT"
    )  # DRAFT, SENT, PAID, OVERDUE, CANCELLED
    subtotal_ex_tax = Column(Numeric(12, 2), nullable=False)
    total_tax = Column(Numeric(12, 2), nullable=False)
    total_inc_tax = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    sales_order = relationship("SalesOrder", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice")

    __table_args__ = (Index("ix_invoice_code", "invoice_number"),)


class InvoiceLine(Base, AuditMixin):
    __tablename__ = "invoice_lines"

    id = uuid_column()
    invoice_id = Column(String(36), ForeignKey("invoices.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    tax_rate = Column(Numeric(5, 2), nullable=False)
    line_total_ex_tax = Column(Numeric(12, 2), nullable=False)
    line_total_inc_tax = Column(Numeric(12, 2), nullable=False)
    sequence = Column(Integer, nullable=False)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    invoice = relationship("Invoice", back_populates="lines")
    product = relationship("Product")


# Pricing Models
class PriceList(Base, AuditMixin):
    __tablename__ = "price_lists"

    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    items = relationship("PriceListItem", back_populates="price_list")

    __table_args__ = (Index("ix_price_list_code", "code"),)


class PriceListItem(Base, AuditMixin):
    __tablename__ = "price_list_items"

    id = uuid_column()
    price_list_id = Column(String(36), ForeignKey("price_lists.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    price_list = relationship("PriceList", back_populates="items")
    product = relationship("Product", back_populates="price_list_items")

    __table_args__ = (
        UniqueConstraint(
            "price_list_id", "product_id", "effective_date", name="uq_price_item_date"
        ),
    )


class CustomerPrice(Base, AuditMixin):
    __tablename__ = "customer_prices"

    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    customer = relationship("Customer", back_populates="customer_prices")
    product = relationship("Product", back_populates="customer_prices")

    __table_args__ = (
        UniqueConstraint(
            "customer_id", "product_id", "effective_date", name="uq_customer_price_date"
        ),
    )


# Packaging Models
class PackUnit(Base, AuditMixin):
    __tablename__ = "pack_units"

    id = uuid_column()
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    conversions_from = relationship(
        "PackConversion",
        foreign_keys="PackConversion.from_unit_id",
        back_populates="from_unit",
    )
    conversions_to = relationship(
        "PackConversion",
        foreign_keys="PackConversion.to_unit_id",
        back_populates="to_unit",
    )

    __table_args__ = (Index("ix_pack_unit_code", "code"),)


class Unit(Base, AuditMixin):
    """Platform-wide units of measurement table."""

    __tablename__ = "units"

    id = uuid_column()
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    symbol = Column(String(10))  # Display symbol (e.g., "kg", "L", "mL")
    unit_type = Column(String(20))  # MASS, VOLUME, COUNT, etc.
    conversion_formula = Column(Text)  # Mathematical formula for conversions
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    __table_args__ = (
        Index("ix_unit_code", "code"),
        Index("ix_unit_type", "unit_type"),
    )


class PackConversion(Base, AuditMixin):
    __tablename__ = "pack_conversions"

    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    from_unit_id = Column(String(36), ForeignKey("pack_units.id"), nullable=False)
    to_unit_id = Column(String(36), ForeignKey("pack_units.id"), nullable=False)
    conversion_factor = Column(Numeric(12, 6), nullable=False)  # Multiplicative factor
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    # Relationships
    product = relationship("Product", back_populates="pack_conversions")
    from_unit = relationship(
        "PackUnit", foreign_keys=[from_unit_id], back_populates="conversions_from"
    )
    to_unit = relationship(
        "PackUnit", foreign_keys=[to_unit_id], back_populates="conversions_to"
    )

    __table_args__ = (
        UniqueConstraint(
            "product_id", "from_unit_id", "to_unit_id", name="uq_pack_conversion"
        ),
    )


# Legacy Data Preservation
class LegacyAcstkData(Base):
    """Store complete legacy acstk record data for reference and migration tracking."""

    __tablename__ = "legacy_acstk_data"

    id = uuid_column()
    product_id = Column(
        String(36), ForeignKey("products.id"), nullable=False, index=True
    )
    legacy_no = Column(Integer)  # Original record number

    # Product Description Fields
    legacy_search = Column(String(50))  # search field
    ean13 = Column(Numeric(18, 4))  # EAN-13 barcode (stored as CURRENCY)
    desc1 = Column(String(50))  # Primary description
    desc2 = Column(String(20))  # Secondary description
    legacy_suplr = Column(String(10))  # Supplier code
    size = Column(String(10))
    legacy_unit = Column(String(10))  # Unit code
    pack = Column(Integer)
    dgflag = Column(String(1))  # Dangerous goods flag
    form = Column(String(10))
    pkge = Column(Integer)
    label = Column(Integer)
    manu = Column(Integer)
    legacy_active = Column(String(1))  # Legacy active status

    # Financial Description Fields
    taxinc = Column(String(1))  # Tax included
    salestaxcde = Column(String(1))
    purcost = Column(Numeric(10, 2))  # Purchase cost
    purtax = Column(Numeric(10, 2))  # Purchase tax
    wholesalecost = Column(Numeric(10, 2))
    disccdeone = Column(String(1))  # Discount code 1
    disccdetwo = Column(String(1))  # Discount code 2

    # Price Codes
    wholesalecde = Column(String(1))
    retailcde = Column(String(1))
    countercde = Column(String(1))
    tradecde = Column(String(1))
    contractcde = Column(String(1))
    industrialcde = Column(String(1))
    distributorcde = Column(String(1))

    # Prices
    retail = Column(Numeric(10, 2))
    counter = Column(Numeric(10, 2))
    trade = Column(Numeric(10, 2))
    contract = Column(Numeric(10, 2))
    industrial = Column(Numeric(10, 2))
    distributor = Column(Numeric(10, 2))

    # Standard Cost References
    suplr4stdcost = Column(String(10))
    search4stdcost = Column(String(50))

    # Stock Holding Fields
    cogs = Column(Numeric(10, 2))  # Cost of goods sold
    gpc = Column(Numeric(10, 2))  # Gross profit cost
    rmc = Column(Numeric(10, 2))  # Raw material cost
    gpr = Column(Numeric(10, 4))  # Gross profit ratio
    soh = Column(Integer)  # Stock on hand
    sohv = Column(Numeric(10, 2))  # Stock on hand value
    sip = Column(Integer)  # Stock in progress
    soo = Column(Integer)  # Stock on order
    sold = Column(Integer)  # Quantity sold
    legacy_date = Column(String(10))  # Last transaction date (YYYYMMDD)

    # Additional Fields
    bulk = Column(Numeric(10, 2))
    lid = Column(Integer)
    pbox = Column(Integer)
    boxlbl = Column(Integer)

    # Metadata
    imported_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)

    # Relationships
    product = relationship("Product")


# Xero Integration Models
class XeroToken(Base):
    """Store Xero OAuth2 access and refresh tokens."""

    __tablename__ = "xero_tokens"

    id = uuid_column()
    access_token = Column(Text, nullable=False)
    refresh_token = Column(Text, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    tenant_id = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class XeroSyncLog(Base):
    """Audit log for Xero sync operations."""

    __tablename__ = "xero_sync_log"

    id = uuid_column()
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)
    object_type = Column(String(50))  # Contact, Item, Bill, Invoice, Journal, BatchPost
    object_id = Column(String(100))  # Local ID or code
    direction = Column(String(10))  # PUSH or PULL
    status = Column(String(20))  # OK, ERROR
    message = Column(Text)

    __table_args__ = (
        Index("ix_sync_log_ts", "ts"),
        Index("ix_sync_log_object", "object_type", "object_id"),
    )


# Excise Rate Model
class ExciseRate(Base, AuditMixin):
    """Excise tax rates over time - allows historical accuracy."""

    __tablename__ = "excise_rates"

    id = uuid_column()
    date_active_from = Column(
        DateTime, nullable=False, index=True
    )  # Date when rate becomes effective
    rate_per_l_abv = Column(Numeric(10, 2), nullable=False)  # Rate in $/L ABV
    description = Column(Text)  # Optional description/notes
    is_active = Column(Boolean, default=True, nullable=False)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    __table_args__ = (
        UniqueConstraint("date_active_from", name="uq_excise_rate_date"),
        Index("ix_excise_rate_active", "is_active", "date_active_from"),
    )


class PurchaseFormat(Base, AuditMixin):
    """Purchase format types (IBC, bag, Bag, Carboy, Drum, Box, etc.)."""

    __tablename__ = "purchase_formats"

    id = uuid_column()
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    # Note: created_at, updated_at, deleted_at, deleted_by, version, versioned_at,
    # versioned_by, previous_version_id, archived_at, archived_by are provided by AuditMixin

    __table_args__ = (Index("ix_purchase_format_code", "code"),)
