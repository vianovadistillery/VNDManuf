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
        ean13=product.ean13,
        supplier_id=str(product.supplier_id) if product.supplier_id else None,
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
    db: Session = Depends(get_db)
):
    """List products with optional search."""
    stmt = select(Product).options(joinedload(Product.variants))
    
    if query:
        stmt = stmt.where(
            Product.name.contains(query) | Product.sku.contains(query)
        )
    
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
        ean13=product_data.ean13,
        supplier_id=product_data.supplier_id,
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
    if product_data.ean13 is not None:
        product.ean13 = product_data.ean13
    if product_data.supplier_id is not None:
        product.supplier_id = product_data.supplier_id
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
