# app/adapters/db/qb_models.py
"""QuickBASIC legacy models for manufacturing system."""

import uuid
from datetime import datetime

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

from app.settings import settings

from .session import Base


def uuid_column():
    """Return appropriate UUID column type based on database."""
    if settings.database.database_url.startswith("postgresql"):
        return Column(uuid.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    else:
        return Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))


# Raw Material Groups
class RawMaterialGroup(Base):
    """Raw material groupings (e.g., Solvents, Resins, Pigments)."""

    __tablename__ = "raw_material_groups"

    id = uuid_column()
    code = Column(String(10), unique=True, nullable=False, index=True)  # e.g., "1.1.1"
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_rm_group_code", "code"),)


# Raw Materials
class RawMaterial(Base):
    """
    Raw materials for manufacturing.
    Maps to RcdFmtmsrmat (41 fields from MSRMAT.INC).
    """

    __tablename__ = "raw_materials"

    id = uuid_column()

    # Identification
    code = Column(Integer, unique=True, nullable=False, index=True)  # Material code
    desc1 = Column(String(25))  # Primary description
    desc2 = Column(String(25))  # Secondary description
    search_key = Column(String(5))  # Quick search key
    search_ext = Column(String(8))  # Extended search

    # Physical Properties
    sg = Column(Numeric(10, 6))  # Specific gravity
    vol_solid = Column(Numeric(10, 6))  # Volume solid
    solid_sg = Column(Numeric(10, 6))  # Solid specific gravity
    wt_solid = Column(Numeric(10, 6))  # Weight solid

    # Purchase Information
    purqty = Column(Integer)  # Purchase quantity
    purchase_cost = Column(Numeric(10, 2))
    purchase_unit = Column(String(2))  # PurUnit
    deal_cost = Column(Numeric(10, 2))
    sup_unit = Column(String(2))
    sup_qty = Column(Numeric(10, 3))

    # Usage Information
    usage_cost = Column(Numeric(10, 2))
    usage_unit = Column(String(2))

    # Grouping
    group_id = Column(String(36), ForeignKey("raw_material_groups.id"))

    # Status
    active_flag = Column(String(1))  # A/S/R/M

    # Stock Management
    soh = Column(Numeric(12, 3))  # Stock on hand
    opening_soh = Column(Numeric(12, 3))
    soh_value = Column(Numeric(12, 2))
    so_on_order = Column(Integer)
    so_in_process = Column(Numeric(12, 3))
    restock_level = Column(Numeric(12, 3))
    used_ytd = Column(Numeric(12, 3))

    # Hazard/Safety
    hazard = Column(String(1))
    condition = Column(String(1))
    msds_flag = Column(String(1))

    # Alternative Materials
    altno1 = Column(Integer)
    altno2 = Column(Integer)
    altno3 = Column(Integer)
    altno4 = Column(Integer)
    altno5 = Column(Integer)

    # Dates
    last_movement_date = Column(String(8))
    last_purchase_date = Column(String(8))

    # Notes
    notes = Column(String(25))

    # Barcode
    ean13 = Column(Numeric(18, 4))

    # Accounting
    xero_account = Column(String(50))

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    group = relationship("RawMaterialGroup")
    suppliers = relationship("RawMaterialSupplier", back_populates="raw_material")

    __table_args__ = (
        Index("ix_raw_material_code", "code"),
        Index("ix_raw_material_desc1", "desc1"),
        Index("ix_raw_material_active", "active_flag"),
    )


class RawMaterialSupplier(Base):
    """Junction table for many-to-many relationship between raw materials and suppliers."""

    __tablename__ = "raw_material_suppliers"

    id = uuid_column()
    raw_material_id = Column(String(36), ForeignKey("raw_materials.id"), nullable=False)
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=False)
    is_primary = Column(Boolean, default=False)
    min_qty = Column(Numeric(12, 3))  # Minimum order quantity
    lead_time_days = Column(Integer)  # Lead time in days
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    raw_material = relationship("RawMaterial", back_populates="suppliers")
    supplier = relationship("Supplier")

    __table_args__ = (
        UniqueConstraint("raw_material_id", "supplier_id", name="uq_rm_supplier"),
        Index("ix_rm_supplier_material", "raw_material_id"),
        Index("ix_rm_supplier_supplier", "supplier_id"),
    )


# Formula Classes
class FormulaClass(Base):
    """Formula classes for categorization and YTD tracking."""

    __tablename__ = "formula_classes"

    id = uuid_column()
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    ytd_amounts = Column(Text)  # JSON string for YTD tracking by year
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_formula_class_name", "name"),)


# Markups
class Markup(Base):
    """Markup definitions for pricing."""

    __tablename__ = "markups"

    id = uuid_column()
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    enabled_flag = Column(String(1))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_markup_code", "code"),)


# Condition Types
class ConditionType(Base):
    """Storage and handling condition types."""

    __tablename__ = "condition_types"

    id = uuid_column()
    code = Column(String(1), unique=True, nullable=False, index=True)
    description = Column(String(100), nullable=False)
    extended_desc = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_condition_type_code", "code"),)


# Datasets
class Dataset(Base):
    """Multi-dataset support (Default, Bristol, Henkel, etc.)."""

    __tablename__ = "datasets"

    id = uuid_column()
    code = Column(
        String(3), unique=True, nullable=False, index=True
    )  # Default, BRI, HEN, etc.
    name = Column(String(50), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (Index("ix_dataset_code", "code"),)


# Manufacturing Config
class ManufacturingConfig(Base):
    """Manufacturing system configuration (single row)."""

    __tablename__ = "manufacturing_config"

    id = uuid_column()
    qtyf = Column(String(10))  # Quantity format
    bchno_width = Column(String(10))
    bch_offset = Column(String(10))
    company_name = Column(String(50))
    site_code = Column(String(10))

    # Max values
    max1 = Column(Numeric(10, 2))
    max2 = Column(Numeric(10, 2))
    max3 = Column(Numeric(10, 2))
    max4 = Column(Numeric(10, 2))
    max5 = Column(Numeric(10, 2))
    max6 = Column(Numeric(10, 2))
    max7 = Column(Numeric(10, 2))
    max8 = Column(Numeric(10, 2))
    max9 = Column(Numeric(10, 2))

    # Flags
    flags1 = Column(String(10))
    flags2 = Column(String(10))
    flags3 = Column(String(10))
    flags4 = Column(String(10))
    flags5 = Column(String(10))
    flags6 = Column(String(10))
    flags7 = Column(String(10))
    flags8 = Column(String(10))

    # Reports
    rep1 = Column(String(10))
    rep2 = Column(String(10))
    rep3 = Column(String(10))
    rep4 = Column(String(10))
    rep5 = Column(String(10))
    rep6 = Column(String(10))

    # Printing
    print_hi1 = Column(String(10))
    db_month_raw = Column(String(10))
    cr_month_raw = Column(String(10))

    # Cost indexes
    cans_idx = Column(Integer)
    label_idx = Column(Integer)
    labour_idx = Column(Integer)

    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
