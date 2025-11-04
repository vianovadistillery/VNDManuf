# app/api/pricing.py
"""Pricing API router."""

from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.db.models import (
    Customer,
    CustomerPrice,
    PriceList,
    PriceListItem,
    Product,
)
from app.api.dto import PricingResolutionResponse
from app.domain.rules import round_money

router = APIRouter(prefix="/pricing", tags=["pricing"])


@router.get("/resolve", response_model=PricingResolutionResponse)
async def resolve_pricing(
    customer_id: str = Query(..., description="Customer ID"),
    product_id: str = Query(..., description="Product ID"),
    pack_unit: Optional[str] = Query(None, description="Pack unit for conversion"),
    db: Session = Depends(get_db),
):
    """
    Resolve pricing for a customer and product.

    Resolution order: customer_price → price_list_item → error
    """
    # Validate customer exists (excluding soft-deleted)
    customer = db.get(Customer, customer_id)
    if not customer or customer.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    # Validate product exists (excluding soft-deleted)
    product = db.get(Product, product_id)
    if not product or product.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    # Try customer-specific price first (excluding soft-deleted)
    customer_price_stmt = (
        select(CustomerPrice)
        .where(
            and_(
                CustomerPrice.customer_id == customer_id,
                CustomerPrice.product_id == product_id,
                CustomerPrice.deleted_at.is_(None),
            )
        )
        .order_by(CustomerPrice.effective_date.desc())
    )
    customer_price = db.execute(customer_price_stmt).scalar_one_or_none()

    if customer_price:
        return PricingResolutionResponse(
            unit_price_ex_tax=round_money(customer_price.unit_price_ex_tax),
            tax_rate=customer.tax_rate or Decimal("10.0"),
            resolution_source="customer_price",
        )

    # Try price list item (excluding soft-deleted)
    price_list_item_stmt = (
        select(PriceListItem)
        .join(PriceList)
        .where(
            and_(
                PriceListItem.product_id == product_id,
                PriceList.is_active.is_(True),
                PriceListItem.deleted_at.is_(None),
                PriceList.deleted_at.is_(None),
            )
        )
        .order_by(PriceListItem.effective_date.desc())
    )
    price_list_item = db.execute(price_list_item_stmt).scalar_one_or_none()

    if price_list_item:
        return PricingResolutionResponse(
            unit_price_ex_tax=round_money(price_list_item.unit_price_ex_tax),
            tax_rate=customer.tax_rate or Decimal("10.0"),
            resolution_source="price_list_item",
        )

    # No price found
    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail=f"No price found for product {product.sku} and customer {customer.code}",
    )
