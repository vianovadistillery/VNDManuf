# app/api/dto.py
"""Pydantic DTOs for API requests and responses."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field


# Common DTOs
class ErrorResponse(BaseModel):
    """Standard error response."""
    error: str
    detail: Optional[str] = None
    field: Optional[str] = None


# Product DTOs
class ProductVariantCreate(BaseModel):
    """Create product variant request."""
    variant_code: str = Field(..., min_length=1, max_length=50)
    variant_name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None


class ProductVariantResponse(BaseModel):
    """Product variant response."""
    id: str
    product_id: str
    variant_code: str
    variant_name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime


class ProductCreate(BaseModel):
    """Create product request."""
    sku: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    product_type: Optional[str] = Field("RAW", pattern="^(RAW|WIP|FINISHED)$")  # Deprecated, use capabilities
    # Product Capabilities (replaces product_type)
    is_purchase: bool = False
    is_sell: bool = False
    is_assemble: bool = False
    ean13: Optional[str] = Field(None, max_length=20)
    supplier_id: Optional[str] = None
    raw_material_group_id: Optional[str] = None
    size: Optional[str] = Field(None, max_length=10)
    base_unit: Optional[str] = Field(None, max_length=10)
    pack: Optional[int] = None
    density_kg_per_l: Optional[Decimal] = Field(None, ge=0)
    abv_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    dgflag: Optional[str] = Field(None, max_length=1)
    form: Optional[str] = Field(None, max_length=10)
    pkge: Optional[int] = None
    label: Optional[int] = None
    manu: Optional[int] = None
    taxinc: Optional[str] = Field(None, max_length=1)
    salestaxcde: Optional[str] = Field(None, max_length=1)
    purcost: Optional[Decimal] = Field(None, ge=0)
    purtax: Optional[Decimal] = Field(None, ge=0)
    wholesalecost: Optional[Decimal] = Field(None, ge=0)
    disccdeone: Optional[str] = Field(None, max_length=1)
    disccdetwo: Optional[str] = Field(None, max_length=1)
    wholesalecde: Optional[str] = Field(None, max_length=1)
    retailcde: Optional[str] = Field(None, max_length=1)
    countercde: Optional[str] = Field(None, max_length=1)
    tradecde: Optional[str] = Field(None, max_length=1)
    contractcde: Optional[str] = Field(None, max_length=1)
    industrialcde: Optional[str] = Field(None, max_length=1)
    distributorcde: Optional[str] = Field(None, max_length=1)
    # Raw Material specific fields
    purchase_unit_id: Optional[str] = None  # Purchase unit from units table
    purchase_volume: Optional[Decimal] = Field(None, ge=0)
    specific_gravity: Optional[Decimal] = Field(None, ge=0)
    vol_solid: Optional[Decimal] = Field(None, ge=0)
    solid_sg: Optional[Decimal] = Field(None, ge=0)
    wt_solid: Optional[Decimal] = Field(None, ge=0)
    usage_unit: Optional[str] = Field(None, max_length=2)
    usage_cost: Optional[Decimal] = Field(None, ge=0)
    restock_level: Optional[Decimal] = Field(None, ge=0)
    used_ytd: Optional[Decimal] = Field(None, ge=0)
    hazard: Optional[str] = Field(None, max_length=1)
    condition: Optional[str] = Field(None, max_length=1)
    msds_flag: Optional[str] = Field(None, max_length=1)
    # Finished Good specific fields
    formula_id: Optional[str] = None
    formula_revision: Optional[int] = None
    # Sales Pricing (inc_gst, ex_gst, excise for each price level)
    retail_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    retail_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    retail_excise: Optional[Decimal] = Field(None, ge=0)
    wholesale_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    wholesale_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    wholesale_excise: Optional[Decimal] = Field(None, ge=0)
    distributor_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    distributor_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    distributor_excise: Optional[Decimal] = Field(None, ge=0)
    counter_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    counter_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    counter_excise: Optional[Decimal] = Field(None, ge=0)
    trade_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    trade_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    trade_excise: Optional[Decimal] = Field(None, ge=0)
    contract_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    contract_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    contract_excise: Optional[Decimal] = Field(None, ge=0)
    industrial_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    industrial_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    industrial_excise: Optional[Decimal] = Field(None, ge=0)
    # Cost Pricing (inc_gst, ex_gst, tax_included flags)
    purchase_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    purchase_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    purchase_tax_included: Optional[bool] = False
    usage_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    usage_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    usage_tax_included: Optional[bool] = False
    manufactured_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    manufactured_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    is_active: bool = True


class ProductUpdate(BaseModel):
    """Update product request."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    product_type: Optional[str] = Field(None, pattern="^(RAW|WIP|FINISHED)$")  # Deprecated
    # Product Capabilities
    is_purchase: Optional[bool] = None
    is_sell: Optional[bool] = None
    is_assemble: Optional[bool] = None
    ean13: Optional[str] = Field(None, max_length=20)
    supplier_id: Optional[str] = None
    raw_material_group_id: Optional[str] = None
    size: Optional[str] = Field(None, max_length=10)
    base_unit: Optional[str] = Field(None, max_length=10)
    pack: Optional[int] = None
    density_kg_per_l: Optional[Decimal] = Field(None, ge=0)
    abv_percent: Optional[Decimal] = Field(None, ge=0, le=100)
    dgflag: Optional[str] = Field(None, max_length=1)
    form: Optional[str] = Field(None, max_length=10)
    pkge: Optional[int] = None
    label: Optional[int] = None
    manu: Optional[int] = None
    taxinc: Optional[str] = Field(None, max_length=1)
    salestaxcde: Optional[str] = Field(None, max_length=1)
    purcost: Optional[Decimal] = Field(None, ge=0)
    purtax: Optional[Decimal] = Field(None, ge=0)
    wholesalecost: Optional[Decimal] = Field(None, ge=0)
    disccdeone: Optional[str] = Field(None, max_length=1)
    disccdetwo: Optional[str] = Field(None, max_length=1)
    wholesalecde: Optional[str] = Field(None, max_length=1)
    retailcde: Optional[str] = Field(None, max_length=1)
    countercde: Optional[str] = Field(None, max_length=1)
    tradecde: Optional[str] = Field(None, max_length=1)
    contractcde: Optional[str] = Field(None, max_length=1)
    industrialcde: Optional[str] = Field(None, max_length=1)
    distributorcde: Optional[str] = Field(None, max_length=1)
    # Raw Material specific fields
    purchase_unit_id: Optional[str] = None  # Purchase unit from units table
    purchase_volume: Optional[Decimal] = Field(None, ge=0)
    specific_gravity: Optional[Decimal] = Field(None, ge=0)
    vol_solid: Optional[Decimal] = Field(None, ge=0)
    solid_sg: Optional[Decimal] = Field(None, ge=0)
    wt_solid: Optional[Decimal] = Field(None, ge=0)
    usage_unit: Optional[str] = Field(None, max_length=2)
    usage_cost: Optional[Decimal] = Field(None, ge=0)
    restock_level: Optional[Decimal] = Field(None, ge=0)
    used_ytd: Optional[Decimal] = Field(None, ge=0)
    hazard: Optional[str] = Field(None, max_length=1)
    condition: Optional[str] = Field(None, max_length=1)
    msds_flag: Optional[str] = Field(None, max_length=1)
    # Finished Good specific fields
    formula_id: Optional[str] = None
    formula_revision: Optional[int] = None
    # Sales Pricing
    retail_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    retail_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    retail_excise: Optional[Decimal] = Field(None, ge=0)
    wholesale_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    wholesale_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    wholesale_excise: Optional[Decimal] = Field(None, ge=0)
    distributor_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    distributor_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    distributor_excise: Optional[Decimal] = Field(None, ge=0)
    counter_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    counter_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    counter_excise: Optional[Decimal] = Field(None, ge=0)
    trade_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    trade_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    trade_excise: Optional[Decimal] = Field(None, ge=0)
    contract_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    contract_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    contract_excise: Optional[Decimal] = Field(None, ge=0)
    industrial_price_inc_gst: Optional[Decimal] = Field(None, ge=0)
    industrial_price_ex_gst: Optional[Decimal] = Field(None, ge=0)
    industrial_excise: Optional[Decimal] = Field(None, ge=0)
    # Cost Pricing
    purchase_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    purchase_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    purchase_tax_included: Optional[bool] = None
    usage_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    usage_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    usage_tax_included: Optional[bool] = None
    manufactured_cost_inc_gst: Optional[Decimal] = Field(None, ge=0)
    manufactured_cost_ex_gst: Optional[Decimal] = Field(None, ge=0)
    is_active: Optional[bool] = None


class ProductResponse(BaseModel):
    """Product response."""
    id: str
    sku: str
    name: str
    description: Optional[str]
    product_type: str  # RAW, WIP, or FINISHED (deprecated)
    # Product Capabilities
    is_purchase: bool
    is_sell: bool
    is_assemble: bool
    ean13: Optional[str]
    supplier_id: Optional[str]
    raw_material_group_id: Optional[str]
    size: Optional[str]
    base_unit: Optional[str]
    pack: Optional[int]
    density_kg_per_l: Optional[Decimal]
    abv_percent: Optional[Decimal]
    dgflag: Optional[str]
    form: Optional[str]
    pkge: Optional[int]
    label: Optional[int]
    manu: Optional[int]
    taxinc: Optional[str]
    salestaxcde: Optional[str]
    purcost: Optional[Decimal]
    purtax: Optional[Decimal]
    wholesalecost: Optional[Decimal]
    disccdeone: Optional[str]
    disccdetwo: Optional[str]
    wholesalecde: Optional[str]
    retailcde: Optional[str]
    countercde: Optional[str]
    tradecde: Optional[str]
    contractcde: Optional[str]
    industrialcde: Optional[str]
    distributorcde: Optional[str]
    # Raw Material specific fields
    purchase_unit_id: Optional[str] = None
    purchase_volume: Optional[Decimal] = None
    specific_gravity: Optional[Decimal] = None
    vol_solid: Optional[Decimal] = None
    solid_sg: Optional[Decimal] = None
    wt_solid: Optional[Decimal] = None
    usage_unit: Optional[str] = None
    usage_cost: Optional[Decimal] = None
    restock_level: Optional[Decimal] = None
    used_ytd: Optional[Decimal] = None
    hazard: Optional[str] = None
    condition: Optional[str] = None
    msds_flag: Optional[str] = None
    # Finished Good specific fields
    formula_id: Optional[str] = None
    formula_revision: Optional[int] = None
    # Sales Pricing
    retail_price_inc_gst: Optional[Decimal] = None
    retail_price_ex_gst: Optional[Decimal] = None
    retail_excise: Optional[Decimal] = None
    wholesale_price_inc_gst: Optional[Decimal] = None
    wholesale_price_ex_gst: Optional[Decimal] = None
    wholesale_excise: Optional[Decimal] = None
    distributor_price_inc_gst: Optional[Decimal] = None
    distributor_price_ex_gst: Optional[Decimal] = None
    distributor_excise: Optional[Decimal] = None
    counter_price_inc_gst: Optional[Decimal] = None
    counter_price_ex_gst: Optional[Decimal] = None
    counter_excise: Optional[Decimal] = None
    trade_price_inc_gst: Optional[Decimal] = None
    trade_price_ex_gst: Optional[Decimal] = None
    trade_excise: Optional[Decimal] = None
    contract_price_inc_gst: Optional[Decimal] = None
    contract_price_ex_gst: Optional[Decimal] = None
    contract_excise: Optional[Decimal] = None
    industrial_price_inc_gst: Optional[Decimal] = None
    industrial_price_ex_gst: Optional[Decimal] = None
    industrial_excise: Optional[Decimal] = None
    # Cost Pricing
    purchase_cost_inc_gst: Optional[Decimal] = None
    purchase_cost_ex_gst: Optional[Decimal] = None
    purchase_tax_included: Optional[bool] = None
    usage_cost_inc_gst: Optional[Decimal] = None
    usage_cost_ex_gst: Optional[Decimal] = None
    usage_tax_included: Optional[bool] = None
    manufactured_cost_inc_gst: Optional[Decimal] = None
    manufactured_cost_ex_gst: Optional[Decimal] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    variants: List[ProductVariantResponse] = []


# Pricing DTOs
class PricingResolutionRequest(BaseModel):
    """Pricing resolution request."""
    customer_id: str
    product_id: str
    pack_unit: Optional[str] = None


class PricingResolutionResponse(BaseModel):
    """Pricing resolution response."""
    unit_price_ex_tax: Decimal
    tax_rate: Decimal
    resolution_source: str  # "customer_price", "price_list_item", "error"


# Packing DTOs
class PackConversionRequest(BaseModel):
    """Pack conversion request."""
    product_id: str
    qty: Decimal = Field(..., gt=0)
    from_unit: str
    to_unit: str


class PackConversionResponse(BaseModel):
    """Pack conversion response."""
    converted_qty: Decimal
    conversion_factor: Decimal
    from_unit: str
    to_unit: str


# Invoice DTOs
class InvoiceLineCreate(BaseModel):
    """Create invoice line request."""
    product_id: str
    quantity_kg: Decimal = Field(..., gt=0)
    unit_price_ex_tax: Decimal = Field(..., ge=0)
    tax_rate: Decimal = Field(..., ge=0, le=100)


class InvoiceCreate(BaseModel):
    """Create invoice request."""
    customer_id: str
    sales_order_id: Optional[str] = None
    invoice_date: Optional[datetime] = None
    due_date: Optional[datetime] = None
    lines: List[InvoiceLineCreate] = Field(..., min_items=1)
    notes: Optional[str] = None


class InvoiceLineResponse(BaseModel):
    """Invoice line response."""
    id: str
    product_id: str
    quantity_kg: Decimal
    unit_price_ex_tax: Decimal
    tax_rate: Decimal
    line_total_ex_tax: Decimal
    line_total_inc_tax: Decimal
    sequence: int


class InvoiceResponse(BaseModel):
    """Invoice response."""
    id: str
    customer_id: str
    sales_order_id: Optional[str]
    invoice_number: str
    invoice_date: datetime
    due_date: Optional[datetime]
    status: str
    subtotal_ex_tax: Decimal
    total_tax: Decimal
    total_inc_tax: Decimal
    notes: Optional[str]
    lines: List[InvoiceLineResponse] = []


class InvoiceIssueRequest(BaseModel):
    """Issue invoice request."""
    notes: Optional[str] = None


# Batch DTOs
class BatchComponentCreate(BaseModel):
    """Create batch component request."""
    ingredient_product_id: str
    lot_id: str
    quantity_kg: Decimal = Field(..., gt=0)


class BatchCreate(BaseModel):
    """Create batch request."""
    work_order_id: str
    batch_code: str = Field(..., min_length=1, max_length=50)
    quantity_kg: Decimal = Field(..., gt=0)
    notes: Optional[str] = None


class BatchComponentResponse(BaseModel):
    """Batch component response."""
    id: str
    ingredient_product_id: str
    lot_id: str
    quantity_kg: Decimal
    unit_cost: Optional[Decimal]


class BatchResponse(BaseModel):
    """Batch response."""
    id: str
    work_order_id: str
    batch_code: str
    quantity_kg: Decimal
    status: str
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    notes: Optional[str]
    components: List[BatchComponentResponse] = []


class BatchFinishRequest(BaseModel):
    """Finish batch request."""
    notes: Optional[str] = None
    create_wip: bool = False
    wip_product_id: Optional[str] = None
    qty_fg_kg: Optional[Decimal] = Field(None, gt=0)


# Print DTOs
class PrintResponse(BaseModel):
    """Print response."""
    content: str
    format: str
    generated_at: datetime


# Raw Material DTOs
class RawMaterialCreate(BaseModel):
    """Create raw material request."""
    code: int
    desc1: str = Field(..., max_length=25)
    desc2: Optional[str] = Field(None, max_length=25)
    search_key: Optional[str] = Field(None, max_length=5)
    search_ext: Optional[str] = Field(None, max_length=8)
    sg: Optional[Decimal] = Field(None, ge=0)
    purchase_cost: Optional[Decimal] = Field(None, ge=0)
    purchase_unit: Optional[str] = Field(None, max_length=2)
    usage_cost: Optional[Decimal] = Field(None, ge=0)
    usage_unit: Optional[str] = Field(None, max_length=2)
    deal_cost: Optional[Decimal] = Field(None, ge=0)
    sup_unit: Optional[str] = Field(None, max_length=2)
    sup_qty: Optional[Decimal] = Field(None, ge=0)
    group_id: Optional[str] = None
    active_flag: str = Field(default="A", max_length=1)
    soh: Optional[Decimal] = Field(None, ge=0)
    restock_level: Optional[Decimal] = Field(None, ge=0)
    hazard: Optional[str] = Field(None, max_length=1)
    condition: Optional[str] = Field(None, max_length=1)
    msds_flag: Optional[str] = Field(None, max_length=1)
    notes: Optional[str] = Field(None, max_length=25)
    xero_account: Optional[str] = Field(None, max_length=50)


class RawMaterialUpdate(BaseModel):
    """Update raw material request."""
    desc1: Optional[str] = Field(None, max_length=25)
    desc2: Optional[str] = Field(None, max_length=25)
    search_key: Optional[str] = Field(None, max_length=5)
    search_ext: Optional[str] = Field(None, max_length=8)
    sg: Optional[Decimal] = Field(None, ge=0)
    purchase_cost: Optional[Decimal] = Field(None, ge=0)
    purchase_unit: Optional[str] = Field(None, max_length=2)
    usage_cost: Optional[Decimal] = Field(None, ge=0)
    usage_unit: Optional[str] = Field(None, max_length=2)
    deal_cost: Optional[Decimal] = Field(None, ge=0)
    sup_unit: Optional[str] = Field(None, max_length=2)
    sup_qty: Optional[Decimal] = Field(None, ge=0)
    group_id: Optional[str] = None
    active_flag: Optional[str] = Field(None, max_length=1)
    soh: Optional[Decimal] = Field(None, ge=0)
    opening_soh: Optional[Decimal] = Field(None, ge=0)
    soh_value: Optional[Decimal] = Field(None, ge=0)
    restock_level: Optional[Decimal] = Field(None, ge=0)
    hazard: Optional[str] = Field(None, max_length=1)
    condition: Optional[str] = Field(None, max_length=1)
    msds_flag: Optional[str] = Field(None, max_length=1)
    notes: Optional[str] = Field(None, max_length=25)
    xero_account: Optional[str] = Field(None, max_length=50)


class RawMaterialResponse(BaseModel):
    """Raw material response."""
    id: str
    code: int
    desc1: str
    desc2: Optional[str]
    search_key: Optional[str]
    search_ext: Optional[str]
    sg: Optional[Decimal]
    purchase_cost: Optional[Decimal]
    purchase_unit: Optional[str]
    usage_cost: Optional[Decimal]
    usage_unit: Optional[str]
    deal_cost: Optional[Decimal]
    sup_unit: Optional[str]
    sup_qty: Optional[Decimal]
    group_id: Optional[str]
    active_flag: str
    soh: Optional[Decimal]
    opening_soh: Optional[Decimal]
    soh_value: Optional[Decimal]
    so_on_order: Optional[int]
    so_in_process: Optional[Decimal]
    restock_level: Optional[Decimal]
    used_ytd: Optional[Decimal]
    hazard: Optional[str]
    condition: Optional[str]
    msds_flag: Optional[str]
    altno1: Optional[int]
    altno2: Optional[int]
    altno3: Optional[int]
    altno4: Optional[int]
    altno5: Optional[int]
    last_movement_date: Optional[str]
    last_purchase_date: Optional[str]
    notes: Optional[str]
    ean13: Optional[Decimal]
    xero_account: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RawMaterialGroupResponse(BaseModel):
    """Raw material group response."""
    id: str
    code: str
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
