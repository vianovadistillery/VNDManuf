# app/api/products.py
"""Products API router."""

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session, selectinload

from app.adapters.db import get_db
from app.adapters.db.models import Product, ProductVariant
from app.api.dto import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductVariantCreate,
    ProductVariantResponse,
)

router = APIRouter(prefix="/products", tags=["products"])


def product_to_response(product: Product) -> ProductResponse:
    """Convert Product model to response DTO."""
    # Use getattr to safely access fields that may not exist in database
    return ProductResponse(
        id=str(product.id),
        sku=product.sku,
        name=product.name,
        description=getattr(product, "description", None),
        # Product Capabilities (computed properties)
        is_purchase=getattr(product, "is_purchase", False),
        is_sell=getattr(product, "is_sell", False),
        is_assemble=getattr(product, "is_assemble", False),
        ean13=getattr(product, "ean13", None),
        supplier_id=(
            str(product.supplier_id) if getattr(product, "supplier_id", None) else None
        ),
        raw_material_group_id=None,  # Deprecated field - always None for backward compatibility
        size=getattr(product, "size", None),
        base_unit=getattr(product, "base_unit", None),
        pack=None,  # Deprecated field - always None for backward compatibility
        density_kg_per_l=getattr(product, "density_kg_per_l", None),
        abv_percent=getattr(product, "abv_percent", None),
        dgflag=getattr(product, "dgflag", None),
        form=getattr(product, "form", None),
        pkge=getattr(product, "pkge", None),
        label=getattr(product, "label", None),
        manu=getattr(product, "manu", None),
        taxinc=getattr(product, "taxinc", None),
        salestaxcde=getattr(product, "salestaxcde", None),
        purcost=getattr(product, "purcost", None),
        purtax=getattr(product, "purtax", None),
        wholesalecost=getattr(product, "wholesalecost", None),
        disccdeone=getattr(product, "disccdeone", None),
        disccdetwo=getattr(product, "disccdetwo", None),
        wholesalecde=getattr(product, "wholesalecde", None),
        retailcde=getattr(product, "retailcde", None),
        countercde=getattr(product, "countercde", None),
        tradecde=getattr(product, "tradecde", None),
        contractcde=getattr(product, "contractcde", None),
        industrialcde=getattr(product, "industrialcde", None),
        distributorcde=getattr(product, "distributorcde", None),
        # Raw Material specific fields (may not exist)
        purchase_unit_id=(
            str(getattr(product, "purchase_unit_id", None))
            if getattr(product, "purchase_unit_id", None)
            else None
        ),
        purchase_format_id=(
            str(getattr(product, "purchase_format_id", None))
            if getattr(product, "purchase_format_id", None)
            else None
        ),
        purchase_quantity=getattr(product, "purchase_quantity", None),
        specific_gravity=getattr(product, "specific_gravity", None),
        vol_solid=getattr(product, "vol_solid", None),
        solid_sg=getattr(product, "solid_sg", None),
        wt_solid=getattr(product, "wt_solid", None),
        usage_unit=getattr(product, "usage_unit", None),
        usage_quantity=getattr(product, "usage_quantity", None),
        usage_cost=getattr(product, "usage_cost", None),
        restock_level=getattr(product, "restock_level", None),
        used_ytd=getattr(product, "used_ytd", None),
        hazard=getattr(product, "hazard", None),
        condition=getattr(product, "condition", None),
        msds_flag=getattr(product, "msds_flag", None),
        # Finished Good specific fields (deprecated - use Assembly section instead)
        formula_id=None,  # Deprecated field - always None for backward compatibility
        formula_revision=None,  # Deprecated field - always None for backward compatibility
        # Sales Pricing (may not exist)
        retail_price_inc_gst=getattr(product, "retail_price_inc_gst", None),
        retail_price_ex_gst=getattr(product, "retail_price_ex_gst", None),
        retail_excise=getattr(product, "retail_excise", None),
        wholesale_price_inc_gst=getattr(product, "wholesale_price_inc_gst", None),
        wholesale_price_ex_gst=getattr(product, "wholesale_price_ex_gst", None),
        wholesale_excise=getattr(product, "wholesale_excise", None),
        distributor_price_inc_gst=getattr(product, "distributor_price_inc_gst", None),
        distributor_price_ex_gst=getattr(product, "distributor_price_ex_gst", None),
        distributor_excise=getattr(product, "distributor_excise", None),
        counter_price_inc_gst=getattr(product, "counter_price_inc_gst", None),
        counter_price_ex_gst=getattr(product, "counter_price_ex_gst", None),
        counter_excise=getattr(product, "counter_excise", None),
        trade_price_inc_gst=getattr(product, "trade_price_inc_gst", None),
        trade_price_ex_gst=getattr(product, "trade_price_ex_gst", None),
        trade_excise=getattr(product, "trade_excise", None),
        contract_price_inc_gst=getattr(product, "contract_price_inc_gst", None),
        contract_price_ex_gst=getattr(product, "contract_price_ex_gst", None),
        contract_excise=getattr(product, "contract_excise", None),
        industrial_price_inc_gst=getattr(product, "industrial_price_inc_gst", None),
        industrial_price_ex_gst=getattr(product, "industrial_price_ex_gst", None),
        industrial_excise=getattr(product, "industrial_excise", None),
        # Cost Pricing (may not exist)
        purchase_cost_inc_gst=getattr(product, "purchase_cost_inc_gst", None),
        purchase_cost_ex_gst=getattr(product, "purchase_cost_ex_gst", None),
        purchase_tax_included=getattr(product, "purchase_tax_included", False) or False,
        usage_cost_inc_gst=getattr(product, "usage_cost_inc_gst", None),
        usage_cost_ex_gst=getattr(product, "usage_cost_ex_gst", None),
        usage_tax_included=getattr(product, "usage_tax_included", False) or False,
        manufactured_cost_inc_gst=getattr(product, "manufactured_cost_inc_gst", None),
        manufactured_cost_ex_gst=getattr(product, "manufactured_cost_ex_gst", None),
        is_active=getattr(product, "is_active", True),
        created_at=getattr(product, "created_at", None),
        updated_at=getattr(product, "updated_at", None),
        variants=[
            ProductVariantResponse(
                id=str(v.id),
                product_id=str(v.product_id),
                variant_code=v.variant_code,
                variant_name=v.variant_name,
                description=v.description,
                is_active=v.is_active,
                created_at=v.created_at,
            )
            for v in product.variants
        ],
    )


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: Optional[int] = 10000,  # Default to 10,000 for non-soft-deleted products
    query: Optional[str] = None,
    is_purchase: Optional[bool] = None,  # Filter by capability
    is_sell: Optional[bool] = None,  # Filter by capability
    is_assemble: Optional[bool] = None,  # Filter by capability
    db: Session = Depends(get_db),
):
    """List products with optional search and filtering.

    Returns up to 10,000 non-soft-deleted products by default.
    Set limit=0 to return all non-soft-deleted products (use with caution).
    """
    try:
        # Use selectinload instead of joinedload to avoid duplicate row issues
        # selectinload loads variants in a separate query, avoiding JOIN duplicates
        stmt = select(Product).options(selectinload(Product.variants))

        # Filter out soft-deleted records
        stmt = stmt.where(Product.deleted_at.is_(None))

        if query:
            stmt = stmt.where(
                Product.name.contains(query) | Product.sku.contains(query)
            )

        # Filter by capabilities (note: these are computed properties, so filter in Python)
        # We'll filter after fetching since these aren't database columns
        # For now, we'll apply filters after fetching

        # Apply limit: default to 10,000, or use specified limit (limit=0 means no limit)
        if limit == 0:
            # limit=0 means return all (no limit) - only apply offset
            stmt = stmt.offset(skip)
        else:
            # Use specified limit or default to 10,000
            effective_limit = limit if limit is not None else 10000
            stmt = stmt.offset(skip).limit(effective_limit)

        # Execute query - no need for unique() with selectinload
        products = db.execute(stmt).scalars().all()

        # Apply capability filters in Python (since they're computed properties)
        if is_purchase is not None:
            products = [
                p for p in products if getattr(p, "is_purchase", False) == is_purchase
            ]
        if is_sell is not None:
            products = [p for p in products if getattr(p, "is_sell", False) == is_sell]
        if is_assemble is not None:
            products = [
                p for p in products if getattr(p, "is_assemble", False) == is_assemble
            ]

        return [product_to_response(p) for p in products]
    except Exception as e:
        # Log the actual error for debugging
        import logging

        logger = logging.getLogger(__name__)
        logger.error(
            f"Error in list_products: {type(e).__name__}: {str(e)}", exc_info=True
        )
        # Re-raise to let error handler catch it
        raise


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get product by ID."""
    stmt = (
        select(Product)
        .options(selectinload(Product.variants))
        .where(Product.id == product_id, Product.deleted_at.is_(None))
    )
    product = db.execute(stmt).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product_to_response(product)


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Get product by SKU."""
    stmt = select(Product).where(Product.sku == sku, Product.deleted_at.is_(None))
    product = db.execute(stmt).scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return product_to_response(product)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if SKU already exists (excluding soft-deleted)
    existing = db.execute(
        select(Product).where(
            Product.sku == product_data.sku, Product.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists",
        )

    product = Product(
        id=str(uuid4()),
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        # Product Capabilities
        is_purchase=product_data.is_purchase,
        is_sell=product_data.is_sell,
        is_assemble=product_data.is_assemble,
        ean13=product_data.ean13,
        supplier_id=product_data.supplier_id,
        # raw_material_group_id removed - deprecated field
        size=product_data.size,
        base_unit=product_data.base_unit,
        # pack removed - deprecated field
        density_kg_per_l=product_data.density_kg_per_l,
        abv_percent=product_data.abv_percent,
        dgflag=product_data.dgflag,
        form=product_data.form,
        pkge=product_data.pkge,
        label=product_data.label,
        manu=product_data.manu,
        taxinc=product_data.taxinc,
        salestaxcde=product_data.salestaxcde,
        purcost=product_data.purcost,
        purtax=product_data.purtax,
        wholesalecost=product_data.wholesalecost,
        disccdeone=product_data.disccdeone,
        disccdetwo=product_data.disccdetwo,
        wholesalecde=product_data.wholesalecde,
        retailcde=product_data.retailcde,
        countercde=product_data.countercde,
        tradecde=product_data.tradecde,
        contractcde=product_data.contractcde,
        industrialcde=product_data.industrialcde,
        distributorcde=product_data.distributorcde,
        # Raw Material specific fields
        purchase_unit_id=product_data.purchase_unit_id,
        purchase_format_id=product_data.purchase_format_id,
        purchase_quantity=(
            product_data.purchase_quantity
            if product_data.purchase_quantity is not None
            else product_data.purchase_volume
        ),  # Use purchase_quantity if provided, otherwise fall back to purchase_volume
        specific_gravity=product_data.specific_gravity,
        vol_solid=product_data.vol_solid,
        solid_sg=product_data.solid_sg,
        wt_solid=product_data.wt_solid,
        usage_unit=product_data.usage_unit,
        usage_quantity=product_data.usage_quantity,
        usage_cost=product_data.usage_cost,
        restock_level=product_data.restock_level,
        used_ytd=product_data.used_ytd,
        hazard=product_data.hazard,
        condition=product_data.condition,
        msds_flag=product_data.msds_flag,
        # formula_id and formula_revision removed - deprecated fields (use Assembly section instead)
        # Sales Pricing
        retail_price_inc_gst=product_data.retail_price_inc_gst,
        retail_price_ex_gst=product_data.retail_price_ex_gst,
        retail_excise=product_data.retail_excise,
        wholesale_price_inc_gst=product_data.wholesale_price_inc_gst,
        wholesale_price_ex_gst=product_data.wholesale_price_ex_gst,
        wholesale_excise=product_data.wholesale_excise,
        distributor_price_inc_gst=product_data.distributor_price_inc_gst,
        distributor_price_ex_gst=product_data.distributor_price_ex_gst,
        distributor_excise=product_data.distributor_excise,
        counter_price_inc_gst=product_data.counter_price_inc_gst,
        counter_price_ex_gst=product_data.counter_price_ex_gst,
        counter_excise=product_data.counter_excise,
        trade_price_inc_gst=product_data.trade_price_inc_gst,
        trade_price_ex_gst=product_data.trade_price_ex_gst,
        trade_excise=product_data.trade_excise,
        contract_price_inc_gst=product_data.contract_price_inc_gst,
        contract_price_ex_gst=product_data.contract_price_ex_gst,
        contract_excise=product_data.contract_excise,
        industrial_price_inc_gst=product_data.industrial_price_inc_gst,
        industrial_price_ex_gst=product_data.industrial_price_ex_gst,
        industrial_excise=product_data.industrial_excise,
        # Cost Pricing
        purchase_cost_inc_gst=product_data.purchase_cost_inc_gst,
        purchase_cost_ex_gst=product_data.purchase_cost_ex_gst,
        purchase_tax_included=product_data.purchase_tax_included or False,
        usage_cost_inc_gst=product_data.usage_cost_inc_gst,
        usage_cost_ex_gst=product_data.usage_cost_ex_gst,
        usage_tax_included=product_data.usage_tax_included or False,
        manufactured_cost_inc_gst=product_data.manufactured_cost_inc_gst,
        manufactured_cost_ex_gst=product_data.manufactured_cost_ex_gst,
        is_active=product_data.is_active,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product_to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str, product_data: ProductUpdate, db: Session = Depends(get_db)
):
    """Update product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Update fields
    if product_data.sku is not None:
        # Check if new SKU already exists (excluding current product and soft-deleted)
        existing = db.execute(
            select(Product).where(
                Product.sku == product_data.sku,
                Product.id != product_id,
                Product.deleted_at.is_(None),
            )
        ).scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Product with SKU '{product_data.sku}' already exists",
            )
        product.sku = product_data.sku
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    # Product Capabilities
    if product_data.is_purchase is not None:
        product.is_purchase = product_data.is_purchase
    if product_data.is_sell is not None:
        product.is_sell = product_data.is_sell
    if product_data.is_assemble is not None:
        product.is_assemble = product_data.is_assemble
    if product_data.ean13 is not None:
        product.ean13 = product_data.ean13
    if product_data.supplier_id is not None:
        product.supplier_id = product_data.supplier_id
    # raw_material_group_id removed - deprecated field
    if product_data.size is not None:
        product.size = product_data.size
    if product_data.base_unit is not None:
        product.base_unit = product_data.base_unit
    # pack removed - deprecated field
    if product_data.density_kg_per_l is not None:
        product.density_kg_per_l = product_data.density_kg_per_l
    if product_data.abv_percent is not None:
        product.abv_percent = product_data.abv_percent
    if product_data.dgflag is not None:
        product.dgflag = product_data.dgflag
    if product_data.form is not None:
        product.form = product_data.form
    if product_data.pkge is not None:
        product.pkge = product_data.pkge
    if product_data.label is not None:
        product.label = product_data.label
    if product_data.manu is not None:
        product.manu = product_data.manu
    if product_data.taxinc is not None:
        product.taxinc = product_data.taxinc
    if product_data.salestaxcde is not None:
        product.salestaxcde = product_data.salestaxcde
    if product_data.purcost is not None:
        product.purcost = product_data.purcost
    if product_data.purtax is not None:
        product.purtax = product_data.purtax
    if product_data.wholesalecost is not None:
        product.wholesalecost = product_data.wholesalecost
    if product_data.disccdeone is not None:
        product.disccdeone = product_data.disccdeone
    if product_data.disccdetwo is not None:
        product.disccdetwo = product_data.disccdetwo
    if product_data.wholesalecde is not None:
        product.wholesalecde = product_data.wholesalecde
    if product_data.retailcde is not None:
        product.retailcde = product_data.retailcde
    if product_data.countercde is not None:
        product.countercde = product_data.countercde
    if product_data.tradecde is not None:
        product.tradecde = product_data.tradecde
    if product_data.contractcde is not None:
        product.contractcde = product_data.contractcde
    if product_data.industrialcde is not None:
        product.industrialcde = product_data.industrialcde
    if product_data.distributorcde is not None:
        product.distributorcde = product_data.distributorcde
    # Raw Material specific fields
    if product_data.purchase_unit_id is not None:
        product.purchase_unit_id = product_data.purchase_unit_id
    if product_data.purchase_format_id is not None:
        product.purchase_format_id = product_data.purchase_format_id
    elif product_data.purchase_format_id is None and hasattr(
        product_data, "purchase_format_id"
    ):
        # Allow clearing purchase_format_id by setting to None
        product.purchase_format_id = None
    if product_data.purchase_quantity is not None:
        product.purchase_quantity = product_data.purchase_quantity
    elif product_data.purchase_volume is not None:
        product.purchase_quantity = (
            product_data.purchase_volume
        )  # Fallback for backward compatibility
    # Note: purchase_cost is not stored in the model - it's calculated from purchase_cost_ex_gst/inc_gst
    if product_data.specific_gravity is not None:
        product.specific_gravity = product_data.specific_gravity
    if product_data.vol_solid is not None:
        product.vol_solid = product_data.vol_solid
    if product_data.solid_sg is not None:
        product.solid_sg = product_data.solid_sg
    if product_data.wt_solid is not None:
        product.wt_solid = product_data.wt_solid
    if product_data.usage_unit is not None:
        product.usage_unit = product_data.usage_unit
    if product_data.usage_quantity is not None:
        product.usage_quantity = product_data.usage_quantity
    if product_data.usage_cost is not None:
        product.usage_cost = product_data.usage_cost
    if product_data.restock_level is not None:
        product.restock_level = product_data.restock_level
    if product_data.used_ytd is not None:
        product.used_ytd = product_data.used_ytd
    if product_data.hazard is not None:
        product.hazard = product_data.hazard
    if product_data.condition is not None:
        product.condition = product_data.condition
    if product_data.msds_flag is not None:
        product.msds_flag = product_data.msds_flag
    # formula_id and formula_revision removed - deprecated fields (use Assembly section instead)
    # Sales Pricing
    if product_data.retail_price_inc_gst is not None:
        product.retail_price_inc_gst = product_data.retail_price_inc_gst
    if product_data.retail_price_ex_gst is not None:
        product.retail_price_ex_gst = product_data.retail_price_ex_gst
    if product_data.retail_excise is not None:
        product.retail_excise = product_data.retail_excise
    if product_data.wholesale_price_inc_gst is not None:
        product.wholesale_price_inc_gst = product_data.wholesale_price_inc_gst
    if product_data.wholesale_price_ex_gst is not None:
        product.wholesale_price_ex_gst = product_data.wholesale_price_ex_gst
    if product_data.wholesale_excise is not None:
        product.wholesale_excise = product_data.wholesale_excise
    if product_data.distributor_price_inc_gst is not None:
        product.distributor_price_inc_gst = product_data.distributor_price_inc_gst
    if product_data.distributor_price_ex_gst is not None:
        product.distributor_price_ex_gst = product_data.distributor_price_ex_gst
    if product_data.distributor_excise is not None:
        product.distributor_excise = product_data.distributor_excise
    if product_data.counter_price_inc_gst is not None:
        product.counter_price_inc_gst = product_data.counter_price_inc_gst
    if product_data.counter_price_ex_gst is not None:
        product.counter_price_ex_gst = product_data.counter_price_ex_gst
    if product_data.counter_excise is not None:
        product.counter_excise = product_data.counter_excise
    if product_data.trade_price_inc_gst is not None:
        product.trade_price_inc_gst = product_data.trade_price_inc_gst
    if product_data.trade_price_ex_gst is not None:
        product.trade_price_ex_gst = product_data.trade_price_ex_gst
    if product_data.trade_excise is not None:
        product.trade_excise = product_data.trade_excise
    if product_data.contract_price_inc_gst is not None:
        product.contract_price_inc_gst = product_data.contract_price_inc_gst
    if product_data.contract_price_ex_gst is not None:
        product.contract_price_ex_gst = product_data.contract_price_ex_gst
    if product_data.contract_excise is not None:
        product.contract_excise = product_data.contract_excise
    if product_data.industrial_price_inc_gst is not None:
        product.industrial_price_inc_gst = product_data.industrial_price_inc_gst
    if product_data.industrial_price_ex_gst is not None:
        product.industrial_price_ex_gst = product_data.industrial_price_ex_gst
    if product_data.industrial_excise is not None:
        product.industrial_excise = product_data.industrial_excise
    # Cost Pricing
    if product_data.purchase_cost_inc_gst is not None:
        product.purchase_cost_inc_gst = product_data.purchase_cost_inc_gst
    if product_data.purchase_cost_ex_gst is not None:
        product.purchase_cost_ex_gst = product_data.purchase_cost_ex_gst
    if product_data.purchase_tax_included is not None:
        product.purchase_tax_included = product_data.purchase_tax_included
    if product_data.usage_cost_inc_gst is not None:
        product.usage_cost_inc_gst = product_data.usage_cost_inc_gst
    if product_data.usage_cost_ex_gst is not None:
        product.usage_cost_ex_gst = product_data.usage_cost_ex_gst
    if product_data.usage_tax_included is not None:
        product.usage_tax_included = product_data.usage_tax_included
    if product_data.manufactured_cost_inc_gst is not None:
        product.manufactured_cost_inc_gst = product_data.manufactured_cost_inc_gst
    if product_data.manufactured_cost_ex_gst is not None:
        product.manufactured_cost_ex_gst = product_data.manufactured_cost_ex_gst
    if product_data.is_active is not None:
        product.is_active = product_data.is_active

    db.commit()
    db.refresh(product)

    return product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Soft delete product (marks as deleted, does not remove from database)."""
    from app.services.audit import soft_delete

    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    soft_delete(db, product)
    db.commit()
    return None


# Product Variants
@router.post(
    "/{product_id}/variants",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_product_variant(
    product_id: str, variant_data: ProductVariantCreate, db: Session = Depends(get_db)
):
    """Create a new product variant."""
    # Check if product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Check if variant code already exists for this product (excluding soft-deleted)
    existing = db.execute(
        select(ProductVariant).where(
            and_(
                ProductVariant.product_id == product_id,
                ProductVariant.variant_code == variant_data.variant_code,
                ProductVariant.deleted_at.is_(None),
            )
        )
    ).scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Variant with code '{variant_data.variant_code}' already exists for this product",
        )

    variant = ProductVariant(
        id=str(uuid4()),
        product_id=product_id,
        variant_code=variant_data.variant_code,
        variant_name=variant_data.variant_name,
        description=variant_data.description,
        is_active=True,
    )

    db.add(variant)
    db.commit()
    db.refresh(variant)

    return ProductVariantResponse(
        id=variant.id,
        product_id=variant.product_id,
        variant_code=variant.variant_code,
        variant_name=variant.variant_name,
        description=variant.description,
        is_active=variant.is_active,
        created_at=variant.created_at,
    )


@router.get("/{product_id}/variants", response_model=List[ProductVariantResponse])
async def list_product_variants(product_id: str, db: Session = Depends(get_db)):
    """List variants for a product."""
    # Check if product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    stmt = select(ProductVariant).where(
        ProductVariant.product_id == product_id, ProductVariant.deleted_at.is_(None)
    )
    variants = db.execute(stmt).scalars().all()

    return [
        ProductVariantResponse(
            id=v.id,
            product_id=v.product_id,
            variant_code=v.variant_code,
            variant_name=v.variant_name,
            description=v.description,
            is_active=v.is_active,
            created_at=v.created_at,
        )
        for v in variants
    ]
