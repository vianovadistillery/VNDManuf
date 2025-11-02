# app/api/products.py
"""Products API router."""

from typing import List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, and_

from app.adapters.db import get_db
from app.adapters.db.models import Product, ProductVariant
from app.api.dto import (
    ProductCreate, ProductUpdate, ProductResponse, ProductVariantCreate, ProductVariantResponse,
    ErrorResponse
)

router = APIRouter(prefix="/products", tags=["products"])


def product_to_response(product: Product) -> ProductResponse:
    """Convert Product model to response DTO."""
    return ProductResponse(
        id=str(product.id),
        sku=product.sku,
        name=product.name,
        description=product.description,
        product_type=product.product_type or "RAW",
        ean13=product.ean13,
        supplier_id=str(product.supplier_id) if product.supplier_id else None,
        raw_material_group_id=str(product.raw_material_group_id) if product.raw_material_group_id else None,
        size=product.size,
        base_unit=product.base_unit,
        pack=product.pack,
        density_kg_per_l=product.density_kg_per_l,
        abv_percent=product.abv_percent,
        dgflag=product.dgflag,
        form=product.form,
        pkge=product.pkge,
        label=product.label,
        manu=product.manu,
        taxinc=product.taxinc,
        salestaxcde=product.salestaxcde,
        purcost=product.purcost,
        purtax=product.purtax,
        wholesalecost=product.wholesalecost,
        disccdeone=product.disccdeone,
        disccdetwo=product.disccdetwo,
        wholesalecde=product.wholesalecde,
        retailcde=product.retailcde,
        countercde=product.countercde,
        tradecde=product.tradecde,
        contractcde=product.contractcde,
        industrialcde=product.industrialcde,
        distributorcde=product.distributorcde,
        # Raw Material specific fields
        purchase_unit_id=str(product.purchase_unit_id) if product.purchase_unit_id else None,
        purchase_volume=product.purchase_volume,
        specific_gravity=product.specific_gravity,
        vol_solid=product.vol_solid,
        solid_sg=product.solid_sg,
        wt_solid=product.wt_solid,
        usage_unit=product.usage_unit,
        usage_cost=product.usage_cost,
        restock_level=product.restock_level,
        used_ytd=product.used_ytd,
        hazard=product.hazard,
        condition=product.condition,
        msds_flag=product.msds_flag,
        # Finished Good specific fields
        formula_id=str(product.formula_id) if product.formula_id else None,
        formula_revision=product.formula_revision,
        is_active=product.is_active,
        created_at=product.created_at,
        updated_at=product.updated_at,
        variants=[
            ProductVariantResponse(
                id=str(v.id),
                product_id=str(v.product_id),
                variant_code=v.variant_code,
                variant_name=v.variant_name,
                description=v.description,
                is_active=v.is_active,
                created_at=v.created_at
            ) for v in product.variants
        ]
    )


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = 0,
    limit: int = 100,
    query: Optional[str] = None,
    product_type: Optional[str] = None,  # Filter by product_type (RAW, WIP, FINISHED)
    db: Session = Depends(get_db)
):
    """List products with optional search and product_type filtering."""
    stmt = select(Product).options(joinedload(Product.variants))
    
    if query:
        stmt = stmt.where(
            Product.name.contains(query) | Product.sku.contains(query)
        )
    
    if product_type:
        stmt = stmt.where(Product.product_type == product_type)
    
    stmt = stmt.offset(skip).limit(limit)
    products = db.execute(stmt).scalars().unique().all()
    
    return [product_to_response(p) for p in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: str, db: Session = Depends(get_db)):
    """Get product by ID."""
    stmt = select(Product).options(joinedload(Product.variants)).where(Product.id == product_id)
    product = db.execute(stmt).scalars().unique().first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product_to_response(product)


@router.get("/sku/{sku}", response_model=ProductResponse)
async def get_product_by_sku(sku: str, db: Session = Depends(get_db)):
    """Get product by SKU."""
    stmt = select(Product).where(Product.sku == sku)
    product = db.execute(stmt).scalar_one_or_none()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return product_to_response(product)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    """Create a new product."""
    # Check if SKU already exists
    existing = db.execute(select(Product).where(Product.sku == product_data.sku)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Product with SKU '{product_data.sku}' already exists"
        )
    
    product = Product(
        id=str(uuid4()),
        sku=product_data.sku,
        name=product_data.name,
        description=product_data.description,
        product_type=product_data.product_type,
        ean13=product_data.ean13,
        supplier_id=product_data.supplier_id,
        raw_material_group_id=product_data.raw_material_group_id,
        size=product_data.size,
        base_unit=product_data.base_unit,
        pack=product_data.pack,
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
        purchase_volume=product_data.purchase_volume,
        specific_gravity=product_data.specific_gravity,
        vol_solid=product_data.vol_solid,
        solid_sg=product_data.solid_sg,
        wt_solid=product_data.wt_solid,
        usage_unit=product_data.usage_unit,
        usage_cost=product_data.usage_cost,
        restock_level=product_data.restock_level,
        used_ytd=product_data.used_ytd,
        hazard=product_data.hazard,
        condition=product_data.condition,
        msds_flag=product_data.msds_flag,
        # Finished Good specific fields
        formula_id=product_data.formula_id,
        formula_revision=product_data.formula_revision,
        is_active=product_data.is_active
    )
    
    db.add(product)
    db.commit()
    db.refresh(product)
    
    return product_to_response(product)


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: str,
    product_data: ProductUpdate,
    db: Session = Depends(get_db)
):
    """Update product."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Update fields
    if product_data.name is not None:
        product.name = product_data.name
    if product_data.description is not None:
        product.description = product_data.description
    if product_data.product_type is not None:
        product.product_type = product_data.product_type
    if product_data.ean13 is not None:
        product.ean13 = product_data.ean13
    if product_data.supplier_id is not None:
        product.supplier_id = product_data.supplier_id
    if product_data.raw_material_group_id is not None:
        product.raw_material_group_id = product_data.raw_material_group_id
    if product_data.size is not None:
        product.size = product_data.size
    if product_data.base_unit is not None:
        product.base_unit = product_data.base_unit
    if product_data.pack is not None:
        product.pack = product_data.pack
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
    if product_data.purchase_volume is not None:
        product.purchase_volume = product_data.purchase_volume
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
    # Finished Good specific fields
    if product_data.formula_id is not None:
        product.formula_id = product_data.formula_id
    if product_data.formula_revision is not None:
        product.formula_revision = product_data.formula_revision
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    db.commit()
    db.refresh(product)
    
    return product_to_response(product)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(product_id: str, db: Session = Depends(get_db)):
    """Delete product (soft delete by setting is_active=False)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    product.is_active = False
    db.commit()


# Product Variants
@router.post("/{product_id}/variants", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED)
async def create_product_variant(
    product_id: str,
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db)
):
    """Create a new product variant."""
    # Check if product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Check if variant code already exists for this product
    existing = db.execute(
        select(ProductVariant).where(
            and_(
                ProductVariant.product_id == product_id,
                ProductVariant.variant_code == variant_data.variant_code
            )
        )
    ).scalar_one_or_none()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Variant with code '{variant_data.variant_code}' already exists for this product"
        )
    
    variant = ProductVariant(
        id=str(uuid4()),
        product_id=product_id,
        variant_code=variant_data.variant_code,
        variant_name=variant_data.variant_name,
        description=variant_data.description,
        is_active=True
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
        created_at=variant.created_at
    )


@router.get("/{product_id}/variants", response_model=List[ProductVariantResponse])
async def list_product_variants(product_id: str, db: Session = Depends(get_db)):
    """List variants for a product."""
    # Check if product exists
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    stmt = select(ProductVariant).where(ProductVariant.product_id == product_id)
    variants = db.execute(stmt).scalars().all()
    
    return [
        ProductVariantResponse(
            id=v.id,
            product_id=v.product_id,
            variant_code=v.variant_code,
            variant_name=v.variant_name,
            description=v.description,
            is_active=v.is_active,
            created_at=v.created_at
        ) for v in variants
    ]
