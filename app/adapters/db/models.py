# app/adapters/db/models.py
"""SQLAlchemy database models."""

import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, ForeignKey, Index, Integer, Numeric, String, Text, UniqueConstraint
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .session import Base
from app.settings import settings


def uuid_column():
    """Return appropriate UUID column type based on database."""
    if settings.database.database_url.startswith("postgresql"):
        return Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Core Product Models
class Product(Base):
    __tablename__ = "products"
    
    id = uuid_column()
    sku = Column(String(50), unique=True, nullable=False, index=True)
    
    # Product Identification
    name = Column(String(200), nullable=False)
    description = Column(Text)
    ean13 = Column(String(20))  # EAN-13 barcode
    supplier_id = Column(String(36), ForeignKey("suppliers.id"))
    xero_item_id = Column(String(100))  # Xero Item UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero
    
    # Physical Properties
    size = Column(String(10))
    base_unit = Column(String(10))  # KG, LT, EA
    pack = Column(Integer)  # Package quantity
    density_kg_per_l = Column(Numeric(10, 6))  # For L to kg conversions
    abv_percent = Column(Numeric(5, 2))  # ABV as % v/v
    
    # Product Classifications
    dgflag = Column(String(1))  # Dangerous goods flag
    form = Column(String(10))  # Form code
    pkge = Column(Integer)  # Package type
    label = Column(Integer)  # Label type
    manu = Column(Integer)  # Manufacturer code
    
    # Financial/Tax
    taxinc = Column(String(1))  # Tax included flag
    salestaxcde = Column(String(1))  # Sales tax code
    purcost = Column(Numeric(10, 2))  # Purchase cost
    purtax = Column(Numeric(10, 2))  # Purchase tax
    wholesalecost = Column(Numeric(10, 2))
    
    # Pricing Codes
    disccdeone = Column(String(1))  # Discount code 1
    disccdetwo = Column(String(1))  # Discount code 2
    wholesalecde = Column(String(1))
    retailcde = Column(String(1))
    countercde = Column(String(1))
    tradecde = Column(String(1))
    contractcde = Column(String(1))
    industrialcde = Column(String(1))
    distributorcde = Column(String(1))
    
    # Status
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    supplier = relationship("Supplier", foreign_keys=[supplier_id])
    variants = relationship("ProductVariant", back_populates="product")
    formulas = relationship("Formula", back_populates="product")
    inventory_lots = relationship("InventoryLot", back_populates="product")
    pack_conversions = relationship("PackConversion", back_populates="product")
    price_list_items = relationship("PriceListItem", back_populates="product")
    customer_prices = relationship("CustomerPrice", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"
    
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    variant_code = Column(String(50), nullable=False)
    variant_name = Column(String(200), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="variants")
    
    __table_args__ = (
        UniqueConstraint("product_id", "variant_code", name="uq_product_variant_code"),
    )


# Formula Models
class Formula(Base):
    __tablename__ = "formulas"
    
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    formula_code = Column(String(50), nullable=False)
    formula_name = Column(String(200), nullable=False)
    version = Column(Integer, default=1)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="formulas")
    lines = relationship("FormulaLine", back_populates="formula")
    
    __table_args__ = (
        UniqueConstraint("product_id", "formula_code", "version", name="uq_formula_version"),
    )


class FormulaLine(Base):
    __tablename__ = "formula_lines"
    
    id = uuid_column()
    formula_id = Column(String(36), ForeignKey("formulas.id"), nullable=False)
    raw_material_id = Column(String(36), ForeignKey("raw_materials.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)  # Canonical storage in kg
    sequence = Column(Integer, nullable=False)
    notes = Column(Text)
    unit = Column(String(10))  # Display unit (kg, g, L, mL, etc.)
    
    # Relationships
    formula = relationship("Formula", back_populates="lines")
    raw_material = relationship("RawMaterial")
    
    __table_args__ = (
        UniqueConstraint("formula_id", "sequence", name="uq_formula_line_sequence"),
    )


# Inventory Models
class InventoryLot(Base):
    __tablename__ = "inventory_lots"
    
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    lot_code = Column(String(50), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)  # Canonical storage in kg
    unit_cost = Column(Numeric(10, 2))  # Cost per kg
    received_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="inventory_lots")
    transactions = relationship("InventoryTxn", back_populates="lot")
    
    __table_args__ = (
        UniqueConstraint("product_id", "lot_code", name="uq_lot_code"),
        Index("ix_lot_product_code", "product_id", "lot_code"),
    )


class InventoryTxn(Base):
    __tablename__ = "inventory_txns"
    
    id = uuid_column()
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=False)
    transaction_type = Column(String(20), nullable=False)  # RECEIPT, ISSUE, ADJUSTMENT
    quantity_kg = Column(Numeric(12, 3), nullable=False)  # Positive for receipts, negative for issues
    unit_cost = Column(Numeric(10, 2))
    reference_type = Column(String(50))  # PURCHASE_ORDER, WORK_ORDER, SALES_ORDER, etc.
    reference_id = Column(String(36))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100))
    
    # Relationships
    lot = relationship("InventoryLot", back_populates="transactions")
    
    __table_args__ = (
        Index("ix_txn_lot_ts", "lot_id", "created_at"),
    )


# Work Order Models
class WorkOrder(Base):
    __tablename__ = "work_orders"
    
    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    formula_id = Column(String(36), ForeignKey("formulas.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    status = Column(String(20), default="DRAFT")  # DRAFT, RELEASED, IN_PROGRESS, COMPLETED, CANCELLED
    created_at = Column(DateTime, default=datetime.utcnow)
    released_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    product = relationship("Product")
    formula = relationship("Formula")
    lines = relationship("WorkOrderLine", back_populates="work_order")
    batches = relationship("Batch", back_populates="work_order")
    
    __table_args__ = (
        Index("ix_work_order_code", "code"),
    )


class WorkOrderLine(Base):
    __tablename__ = "work_order_lines"
    
    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    ingredient_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    required_quantity_kg = Column(Numeric(12, 3), nullable=False)
    allocated_quantity_kg = Column(Numeric(12, 3), default=0)
    sequence = Column(Integer, nullable=False)
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="lines")
    ingredient_product = relationship("Product", foreign_keys=[ingredient_product_id])


# Batch Models
class Batch(Base):
    __tablename__ = "batches"
    
    id = uuid_column()
    work_order_id = Column(String(36), ForeignKey("work_orders.id"), nullable=False)
    batch_code = Column(String(50), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    status = Column(String(20), default="DRAFT")  # DRAFT, IN_PROGRESS, COMPLETED, CANCELLED
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    notes = Column(Text)
    
    # Extended status for new workflow
    batch_status = Column(String(20), default="planned")  # planned, in_process, closed
    
    # Actual production results
    yield_actual = Column(Numeric(12, 3))  # Actual yield in kg
    yield_litres = Column(Numeric(12, 3))  # Actual yield in litres
    variance_percent = Column(Numeric(5, 2))  # Variance percentage
    
    # Relationships
    work_order = relationship("WorkOrder", back_populates="batches")
    components = relationship("BatchComponent", back_populates="batch")
    qc_results = relationship("QcResult", back_populates="batch")
    batch_lines = relationship("BatchLine", back_populates="batch", cascade="all, delete-orphan")
    
    __table_args__ = (
        UniqueConstraint("work_order_id", "batch_code", name="uq_batch_code"),
        Index("ix_batch_wo_code", "work_order_id", "batch_code"),
    )


class BatchComponent(Base):
    __tablename__ = "batch_components"
    
    id = uuid_column()
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
    ingredient_product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    lot_id = Column(String(36), ForeignKey("inventory_lots.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_cost = Column(Numeric(10, 2))
    
    # Relationships
    batch = relationship("Batch", back_populates="components")
    ingredient_product = relationship("Product", foreign_keys=[ingredient_product_id])
    lot = relationship("InventoryLot")


# Finished Goods Models
class FinishedGood(Base):
    """Finished goods - sellable products."""
    __tablename__ = "finished_goods"
    
    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    description = Column(String(200), nullable=False)
    base_unit = Column(String(10), nullable=False, default="LT")  # LT or KG
    formula_id = Column(String(36), ForeignKey("formulas.id"))  # Optional link to default formula
    formula_revision = Column(Integer)  # Formula revision
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory = relationship("FinishedGoodInventory", back_populates="finished_good", uselist=False)


class FinishedGoodInventory(Base):
    """Stock on hand for finished goods."""
    __tablename__ = "finished_goods_inventory"
    
    fg_id = Column(String(36), ForeignKey("finished_goods.id", ondelete="CASCADE"), primary_key=True)
    soh = Column(Numeric(12, 3), nullable=False, default=0)
    
    # Relationships
    finished_good = relationship("FinishedGood", back_populates="inventory")


class BatchLine(Base):
    """Snapshot of materials used in a batch."""
    __tablename__ = "batch_lines"
    
    id = uuid_column()
    batch_id = Column(String(36), ForeignKey("batches.id", ondelete="CASCADE"), nullable=False)
    material_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    role = Column(String(50))  # resin/solvent/additive/etc
    qty_theoretical = Column(Numeric(12, 3), nullable=False)  # From formula scaled by yield
    qty_actual = Column(Numeric(12, 3))  # Entered/adjusted at execution
    unit = Column(String(10), nullable=False)  # KG/LT/EA
    cost_at_time = Column(Numeric(10, 2))  # Cost capture
    
    # Relationships
    batch = relationship("Batch")
    material = relationship("Product")
    
    __table_args__ = (
        UniqueConstraint("batch_id", "material_id", name="uq_batch_line"),
        Index("ix_batch_line_batch", "batch_id"),
    )


class InventoryMovement(Base):
    """Single source of truth ledger for all stock changes."""
    __tablename__ = "inventory_movements"
    
    id = uuid_column()
    ts = Column(DateTime, nullable=False, default=datetime.utcnow)  # UTC timestamp
    date = Column(String(10), nullable=False)  # Business date (YYYY-MM-DD)
    item_type = Column(String(10), nullable=False)  # RAW or FG
    item_id = Column(String(36), nullable=False)  # Points to products.id (RAW) or finished_goods.id (FG)
    qty = Column(Numeric(12, 3), nullable=False)  # Positive magnitude
    unit = Column(String(10), nullable=False)
    direction = Column(String(10), nullable=False)  # IN or OUT
    source_batch_id = Column(String(36), ForeignKey("batches.id"))
    note = Column(Text)
    
    # Relationships
    batch = relationship("Batch")
    
    __table_args__ = (
        Index("ix_movements_item", "item_type", "item_id"),
        Index("ix_movements_date", "date"),
        Index("ix_movements_batch", "source_batch_id"),
    )


class QcResult(Base):
    __tablename__ = "qc_results"
    
    id = uuid_column()
    batch_id = Column(String(36), ForeignKey("batches.id"), nullable=False)
    test_name = Column(String(100), nullable=False)
    test_value = Column(Numeric(12, 3))
    test_unit = Column(String(20))
    pass_fail = Column(Boolean)
    tested_at = Column(DateTime, default=datetime.utcnow)
    tested_by = Column(String(100))
    notes = Column(Text)
    
    # Relationships
    batch = relationship("Batch", back_populates="qc_results")


# Supplier and Purchase Order Models
class Supplier(Base):
    __tablename__ = "suppliers"
    
    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(200), nullable=False)
    contact_person = Column(String(100))
    email = Column(String(200))
    phone = Column(String(50))
    address = Column(Text)
    xero_contact_id = Column(String(100))  # Xero Contact UUID
    last_sync = Column(DateTime)  # Last successful sync to Xero
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    purchase_orders = relationship("PurchaseOrder", back_populates="supplier")
    
    __table_args__ = (
        Index("ix_supplier_code", "code"),
    )


class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"
    
    id = uuid_column()
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False)
    po_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default="DRAFT")  # DRAFT, SENT, RECEIVED, CANCELLED
    order_date = Column(DateTime, default=datetime.utcnow)
    expected_date = Column(DateTime)
    received_date = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    supplier = relationship("Supplier", back_populates="purchase_orders")
    lines = relationship("PoLine", back_populates="purchase_order")
    
    __table_args__ = (
        Index("ix_purchase_order_po_number", "po_number"),
    )


class PoLine(Base):
    __tablename__ = "po_lines"
    
    id = uuid_column()
    purchase_order_id = Column(String(36), ForeignKey("purchase_orders.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    quantity_kg = Column(Numeric(12, 3), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    line_total = Column(Numeric(12, 2), nullable=False)
    sequence = Column(Integer, nullable=False)
    
    # Relationships
    purchase_order = relationship("PurchaseOrder", back_populates="lines")
    product = relationship("Product")


# Customer and Sales Order Models
class Customer(Base):
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
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    sales_orders = relationship("SalesOrder", back_populates="customer")
    invoices = relationship("Invoice", back_populates="customer")
    customer_prices = relationship("CustomerPrice", back_populates="customer")
    
    __table_args__ = (
        Index("ix_customer_code", "code"),
    )


class SalesOrder(Base):
    __tablename__ = "sales_orders"
    
    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    so_number = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(String(20), default="DRAFT")  # DRAFT, CONFIRMED, SHIPPED, INVOICED, CANCELLED
    order_date = Column(DateTime, default=datetime.utcnow)
    requested_date = Column(DateTime)
    shipped_date = Column(DateTime)
    notes = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="sales_orders")
    lines = relationship("SoLine", back_populates="sales_order")
    invoices = relationship("Invoice", back_populates="sales_order")
    
    __table_args__ = (
        Index("ix_sales_order_so_number", "so_number"),
    )


class SoLine(Base):
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
    
    # Relationships
    sales_order = relationship("SalesOrder", back_populates="lines")
    product = relationship("Product")


# Invoice Models
class Invoice(Base):
    __tablename__ = "invoices"
    
    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    sales_order_id = Column(String(36), ForeignKey("sales_orders.id"))
    invoice_number = Column(String(50), unique=True, nullable=False, index=True)
    invoice_date = Column(DateTime, default=datetime.utcnow)
    due_date = Column(DateTime)
    status = Column(String(20), default="DRAFT")  # DRAFT, SENT, PAID, OVERDUE, CANCELLED
    subtotal_ex_tax = Column(Numeric(12, 2), nullable=False)
    total_tax = Column(Numeric(12, 2), nullable=False)
    total_inc_tax = Column(Numeric(12, 2), nullable=False)
    notes = Column(Text)
    
    # Relationships
    customer = relationship("Customer", back_populates="invoices")
    sales_order = relationship("SalesOrder", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice")
    
    __table_args__ = (
        Index("ix_invoice_code", "invoice_number"),
    )


class InvoiceLine(Base):
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
    
    # Relationships
    invoice = relationship("Invoice", back_populates="lines")
    product = relationship("Product")


# Pricing Models
class PriceList(Base):
    __tablename__ = "price_lists"
    
    id = uuid_column()
    code = Column(String(50), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    items = relationship("PriceListItem", back_populates="price_list")
    
    __table_args__ = (
        Index("ix_price_list_code", "code"),
    )


class PriceListItem(Base):
    __tablename__ = "price_list_items"
    
    id = uuid_column()
    price_list_id = Column(String(36), ForeignKey("price_lists.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    
    # Relationships
    price_list = relationship("PriceList", back_populates="items")
    product = relationship("Product", back_populates="price_list_items")
    
    __table_args__ = (
        UniqueConstraint("price_list_id", "product_id", "effective_date", name="uq_price_item_date"),
    )


class CustomerPrice(Base):
    __tablename__ = "customer_prices"
    
    id = uuid_column()
    customer_id = Column(String(36), ForeignKey("customers.id"), nullable=False)
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    unit_price_ex_tax = Column(Numeric(10, 2), nullable=False)
    effective_date = Column(DateTime, nullable=False)
    expiry_date = Column(DateTime)
    
    # Relationships
    customer = relationship("Customer", back_populates="customer_prices")
    product = relationship("Product", back_populates="customer_prices")
    
    __table_args__ = (
        UniqueConstraint("customer_id", "product_id", "effective_date", name="uq_customer_price_date"),
    )


# Packaging Models
class PackUnit(Base):
    __tablename__ = "pack_units"
    
    id = uuid_column()
    code = Column(String(20), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversions_from = relationship("PackConversion", foreign_keys="PackConversion.from_unit_id", back_populates="from_unit")
    conversions_to = relationship("PackConversion", foreign_keys="PackConversion.to_unit_id", back_populates="to_unit")
    
    __table_args__ = (
        Index("ix_pack_unit_code", "code"),
    )


class PackConversion(Base):
    __tablename__ = "pack_conversions"
    
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    from_unit_id = Column(String(36), ForeignKey("pack_units.id"), nullable=False)
    to_unit_id = Column(String(36), ForeignKey("pack_units.id"), nullable=False)
    conversion_factor = Column(Numeric(12, 6), nullable=False)  # Multiplicative factor
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    product = relationship("Product", back_populates="pack_conversions")
    from_unit = relationship("PackUnit", foreign_keys=[from_unit_id], back_populates="conversions_from")
    to_unit = relationship("PackUnit", foreign_keys=[to_unit_id], back_populates="conversions_to")
    
    __table_args__ = (
        UniqueConstraint("product_id", "from_unit_id", "to_unit_id", name="uq_pack_conversion"),
    )


# Legacy Data Preservation
class LegacyAcstkData(Base):
    """Store complete legacy acstk record data for reference and migration tracking."""
    __tablename__ = "legacy_acstk_data"
    
    id = uuid_column()
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False, index=True)
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