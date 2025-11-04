# Complete Product Model (Generated from Database Schema)
# This model includes all 72+ columns from the database


from sqlalchemy import (
    Column,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
)

from app.adapters.db.base import Base
from app.adapters.db.models import uuid_column


class Product(Base):
    __tablename__ = "products"

    # Primary Key - CRITICAL: Must be defined
    id = uuid_column()  # Primary key

    # Core Identification
    sku = Column(String(), nullable=True, index=True)
    name = Column(String(), nullable=True)
    description = Column(String(), nullable=True)
    ean13 = Column(String(), nullable=True)

    # Product Type and Classification
    product_type = Column(String(), nullable=True)
    is_purchase = Column(Numeric(10, 2)(), nullable=True)
    is_sell = Column(Numeric(10, 2)(), nullable=True)
    is_assemble = Column(Numeric(10, 2)(), nullable=True)
    is_tracked = Column(Numeric(10, 2)(), nullable=True)
    sellable = Column(Numeric(10, 2)(), nullable=True)
    is_archived = Column(Numeric(10, 2)(), nullable=True)
    archived_at = Column(Numeric(10, 2)(), nullable=True)

    # Raw Material Fields (RAW product type)
    raw_material_code = Column(Integer(), nullable=True, index=True)
    raw_material_group_id = Column(String(), nullable=True, index=True)
    raw_material_search_key = Column(String(), nullable=True)
    raw_material_search_ext = Column(String(), nullable=True)
    specific_gravity = Column(Numeric(10, 2)(), nullable=True)
    vol_solid = Column(Numeric(10, 2)(), nullable=True)
    solid_sg = Column(Numeric(10, 2)(), nullable=True)
    wt_solid = Column(Numeric(10, 2)(), nullable=True)
    usage_cost = Column(Numeric(10, 2)(), nullable=True)
    usage_unit = Column(String(), nullable=True)
    restock_level = Column(Numeric(10, 2)(), nullable=True)
    used_ytd = Column(Numeric(10, 2)(), nullable=True)
    hazard = Column(String(), nullable=True)
    condition = Column(String(), nullable=True)
    msds_flag = Column(String(), nullable=True)
    altno1 = Column(Integer(), nullable=True)
    altno2 = Column(Integer(), nullable=True)
    altno3 = Column(Integer(), nullable=True)
    altno4 = Column(Integer(), nullable=True)
    altno5 = Column(Integer(), nullable=True)
    last_movement_date = Column(String(), nullable=True)
    last_purchase_date = Column(String(), nullable=True)
    ean13_raw = Column(Numeric(10, 2)(), nullable=True)
    xero_account = Column(String(), nullable=True)

    # Finished Goods Fields (FINISHED product type)
    formula_id = Column(String(), nullable=True)
    formula_revision = Column(Integer(), nullable=True)

    # Physical Properties
    size = Column(String(), nullable=True)
    base_unit = Column(String(), nullable=True)
    pack = Column(Integer(), nullable=True)
    density_kg_per_l = Column(Numeric(10, 2)(), nullable=True)
    abv_percent = Column(Numeric(10, 2)(), nullable=True)

    # Purchase Information
    supplier_id = Column(String(36), ForeignKey("suppliers.id"), nullable=True)
    purchase_unit_id = Column(String(), nullable=True)
    purchase_volume = Column(Numeric(10, 2)(), nullable=True)
    purchase_cost_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    purchase_cost_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    purchase_tax_included = Column(String(), nullable=True)
    purchase_tax_included_bool = Column(String(), nullable=True)
    purcost = Column(Numeric(10, 2)(), nullable=True)
    purtax = Column(Numeric(10, 2)(), nullable=True)

    # Usage Information
    usage_cost_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    usage_cost_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    usage_tax_included = Column(String(), nullable=True)

    # Costing Information
    standard_cost = Column(Numeric(10, 2)(), nullable=True)
    estimated_cost = Column(Numeric(10, 2)(), nullable=True)
    estimate_reason = Column(String(), nullable=True)
    estimated_by = Column(String(), nullable=True)
    estimated_at = Column(Numeric(10, 2)(), nullable=True)
    manufactured_cost_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    manufactured_cost_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    manufactured_tax_included = Column(String(), nullable=True)
    wholesalecost = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Retail
    retail_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    retail_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    retail_excise = Column(Numeric(10, 2)(), nullable=True)
    retailcde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Wholesale
    wholesale_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    wholesale_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    wholesale_excise = Column(Numeric(10, 2)(), nullable=True)
    wholesalecde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Counter
    counter_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    counter_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    counter_excise = Column(Numeric(10, 2)(), nullable=True)
    countercde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Trade
    trade_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    trade_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    trade_excise = Column(Numeric(10, 2)(), nullable=True)
    tradecde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Contract
    contract_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    contract_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    contract_excise = Column(Numeric(10, 2)(), nullable=True)
    contractcde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Industrial
    industrial_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    industrial_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    industrial_excise = Column(Numeric(10, 2)(), nullable=True)
    industrialcde = Column(Numeric(10, 2)(), nullable=True)

    # Pricing - Distributor
    distributor_price_ex_gst = Column(Numeric(10, 2)(), nullable=True)
    distributor_price_inc_gst = Column(Numeric(10, 2)(), nullable=True)
    distributor_excise = Column(Numeric(10, 2)(), nullable=True)
    distributorcde = Column(Numeric(10, 2)(), nullable=True)

    # Product Flags
    dgflag = Column(String(), nullable=True)
    form = Column(String(), nullable=True)
    pkge = Column(Integer(), nullable=True)
    label = Column(Integer(), nullable=True)
    manu = Column(Integer(), nullable=True)
    taxinc = Column(String(), nullable=True)
    salestaxcde = Column(String(), nullable=True)

    # Discount Codes
    disccdeone = Column(String(), nullable=True)
    disccdetwo = Column(String(), nullable=True)

    # Xero Integration
    xero_item_id = Column(String(), nullable=True)
    last_sync = Column(Numeric(10, 2)(), nullable=True)

    # Status and Timestamps
    is_active = Column(Numeric(10, 2)(), nullable=True)
    created_at = Column(Numeric(10, 2)(), nullable=True)
    updated_at = Column(Numeric(10, 2)(), nullable=True)

    __table_args__ = (
        Index("ix_products_sku", "sku"),
        Index("ix_products_product_type", "product_type"),
        Index("ix_products_raw_material_code", "raw_material_code"),
        Index("ix_products_raw_material_group", "raw_material_group_id"),
    )
