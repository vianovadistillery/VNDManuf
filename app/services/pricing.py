# app/services/pricing.py
"""Pricing service - Price resolution and calculation."""

from decimal import Decimal
from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Session
from sqlalchemy import select, and_

from app.adapters.db.models import (
    Customer, Product, CustomerPrice, PriceListItem, PriceList
)
from app.domain.rules import round_money


class PricingService:
    """
    Service for price resolution and calculation.
    
    Resolution order: customer_price → price_list_item → error
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def resolve_price(
        self,
        customer_id: str,
        product_id: str
    ) -> dict:
        """
        Resolve pricing for a customer and product.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            
        Returns:
            Dict with unit_price_ex_tax, tax_rate, resolution_source
            
        Raises:
            ValueError: If customer or product not found, or no price found
        """
        # Validate customer exists
        customer = self.db.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Validate product exists
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Try customer-specific price first
        customer_price = self.db.execute(
            select(CustomerPrice).where(
                and_(
                    CustomerPrice.customer_id == customer_id,
                    CustomerPrice.product_id == product_id
                )
            ).order_by(CustomerPrice.effective_date.desc())
        ).scalar_one_or_none()
        
        if customer_price:
            return {
                'unit_price_ex_tax': round_money(customer_price.unit_price_ex_tax),
                'tax_rate': customer.tax_rate or Decimal("10.0"),
                'resolution_source': 'customer_price'
            }
        
        # Try price list item
        price_list_item = self.db.execute(
            select(PriceListItem)
            .join(PriceList)
            .where(
                and_(
                    PriceListItem.product_id == product_id,
                    PriceList.is_active == True
                )
            )
            .order_by(PriceListItem.effective_date.desc())
        ).scalar_one_or_none()
        
        if price_list_item:
            return {
                'unit_price_ex_tax': round_money(price_list_item.unit_price_ex_tax),
                'tax_rate': customer.tax_rate or Decimal("10.0"),
                'resolution_source': 'price_list_item'
            }
        
        # No price found
        raise ValueError(f"No price found for product {product.sku} and customer {customer.code}")
    
    def calculate_line_total(
        self,
        quantity_kg: Decimal,
        unit_price_ex_tax: Decimal,
        tax_rate: Decimal
    ) -> dict:
        """
        Calculate invoice/sales order line totals.
        
        Args:
            quantity_kg: Quantity in kg
            unit_price_ex_tax: Unit price excluding tax
            tax_rate: Tax rate as percentage (e.g., 10.0 for 10%)
            
        Returns:
            Dict with line_total_ex_tax, tax_amount, line_total_inc_tax
        """
        from app.domain.rules import calculate_line_totals
        
        line_total_ex_tax, tax_amount, line_total_inc_tax = calculate_line_totals(
            quantity_kg, unit_price_ex_tax, tax_rate
        )
        
        return {
            'line_total_ex_tax': line_total_ex_tax,
            'tax_amount': tax_amount,
            'line_total_inc_tax': line_total_inc_tax
        }
    
    def set_customer_price(
        self,
        customer_id: str,
        product_id: str,
        unit_price_ex_tax: Decimal,
        effective_date: Optional[datetime] = None,
        expiry_date: Optional[datetime] = None
    ) -> CustomerPrice:
        """
        Set customer-specific price.
        
        Args:
            customer_id: Customer ID
            product_id: Product ID
            unit_price_ex_tax: Unit price excluding tax
            effective_date: Effective date (defaults to now)
            expiry_date: Optional expiry date
            
        Returns:
            Created CustomerPrice
            
        Raises:
            ValueError: If customer or product not found
        """
        # Validate customer and product
        customer = self.db.get(Customer, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        
        # Create customer price
        customer_price = CustomerPrice(
            customer_id=customer_id,
            product_id=product_id,
            unit_price_ex_tax=round_money(unit_price_ex_tax),
            effective_date=effective_date or datetime.utcnow(),
            expiry_date=expiry_date
        )
        
        self.db.add(customer_price)
        self.db.flush()
        
        return customer_price


def resolve_price(customer_id: str, product_id: str, db: Session) -> dict:
    """Convenience function to resolve price."""
    service = PricingService(db)
    return service.resolve_price(customer_id, product_id)


def calculate_line_total(
    quantity_kg: Decimal,
    unit_price_ex_tax: Decimal,
    tax_rate: Decimal
) -> dict:
    """Convenience function to calculate line totals."""
    # Can't instantiate without db session, so we'll use domain rules directly
    from app.domain.rules import calculate_line_totals
    
    line_total_ex_tax, tax_amount, line_total_inc_tax = calculate_line_totals(
        quantity_kg, unit_price_ex_tax, tax_rate
    )
    
    return {
        'line_total_ex_tax': line_total_ex_tax,
        'tax_amount': tax_amount,
        'line_total_inc_tax': line_total_inc_tax
    }
