"""Shopify order import service - imports orders from Shopify and creates SalesOrders."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.adapters.db.models import Customer, Product
from app.adapters.shopify_client import ShopifyClient
from app.domain.rules import fifo_peek_cost
from app.services.inventory import InventoryService
from apps.vndmanuf_sales.models import (
    SalesChannel,
    SalesOrder,
    SalesOrderLine,
    SalesOrderSource,
    SalesOrderStatus,
)


class ShopifyOrderImportService:
    """Service for importing Shopify orders into the sales system."""

    def __init__(self, db: Session, client: Optional[ShopifyClient] = None):
        self.db = db
        self.client = client or ShopifyClient()
        self.inventory = InventoryService(db)

    def calculate_cogs(
        self, product_id: str, quantity_kg: Decimal
    ) -> Tuple[Decimal, Decimal]:
        """
        Calculate COGS for a product using FIFO costs.

        Args:
            product_id: Product ID
            quantity_kg: Quantity in kg

        Returns:
            Tuple of (cogs_per_unit, cogs_total)
        """
        lots = self.inventory.get_lots_fifo(product_id)
        if not lots:
            # No stock available, return zero cost
            return Decimal("0"), Decimal("0")

        # Get FIFO unit cost (peek without consuming)
        unit_cost = fifo_peek_cost(lots)
        if unit_cost is None:
            return Decimal("0"), Decimal("0")

        cogs_per_unit = unit_cost
        cogs_total = cogs_per_unit * quantity_kg

        return cogs_per_unit, cogs_total

    def _get_or_create_shopify_channel(self) -> SalesChannel:
        """Get or create the Shopify sales channel."""
        channel = (
            self.db.execute(
                select(SalesChannel).where(
                    func.lower(SalesChannel.code) == "shopify",
                    SalesChannel.deleted_at.is_(None),
                )
            )
            .scalars()
            .first()
        )

        if not channel:
            channel = SalesChannel(
                id=str(uuid4()),
                code="SHOPIFY",
                name="Shopify",
                description="Online sales via Shopify",
            )
            self.db.add(channel)
            self.db.flush()

        return channel

    def _get_or_create_customer(self, shopify_customer: Dict[str, Any]) -> Customer:
        """
        Get or create a customer from Shopify customer data.

        Args:
            shopify_customer: Shopify customer dictionary

        Returns:
            Customer model instance
        """
        email = shopify_customer.get("email")
        first_name = shopify_customer.get("first_name", "")
        last_name = shopify_customer.get("last_name", "")

        # Try to find by email first
        if email:
            customer = (
                self.db.execute(
                    select(Customer).where(
                        func.lower(Customer.email) == email.lower(),
                        Customer.deleted_at.is_(None),
                    )
                )
                .scalars()
                .first()
            )
            if customer:
                return customer

        # Try to find by name
        customer_name = (
            f"{first_name} {last_name}".strip() or email or "Unknown Customer"
        )
        customer = (
            self.db.execute(
                select(Customer).where(
                    func.lower(Customer.name) == customer_name.lower(),
                    Customer.deleted_at.is_(None),
                )
            )
            .scalars()
            .first()
        )

        if customer:
            return customer

        # Create new customer
        customer_code = f"SHOPIFY-{shopify_customer.get('id', uuid4())}"
        customer = Customer(
            id=str(uuid4()),
            code=customer_code,
            name=customer_name,
            email=email,
            customer_type="direct_customer",
            is_active=True,
        )
        self.db.add(customer)
        self.db.flush()

        return customer

    def _find_product_by_sku(self, sku: str) -> Optional[Product]:
        """Find a product by SKU."""
        product = (
            self.db.execute(
                select(Product).where(
                    func.lower(Product.sku) == sku.lower(),
                    Product.deleted_at.is_(None),
                )
            )
            .scalars()
            .first()
        )
        return product

    def _find_product_by_variant_id(self, variant_id: str) -> Optional[Product]:
        """Find a product by Shopify variant ID via product_channel_links."""
        from app.adapters.db.models_assemblies_shopify import ProductChannelLink

        link = (
            self.db.query(ProductChannelLink)
            .filter_by(shopify_variant_id=str(variant_id), channel="shopify")
            .first()
        )

        if link:
            return self.db.get(Product, link.product_id)
        return None

    def import_order(self, shopify_order: Dict[str, Any]) -> Tuple[SalesOrder, bool]:
        """
        Import a single Shopify order.

        Args:
            shopify_order: Shopify order dictionary

        Returns:
            Tuple of (SalesOrder, created: bool)
        """
        shopify_order_id = str(shopify_order.get("id"))
        order_ref = f"SHOPIFY-{shopify_order_id}"

        # Check if order already exists
        existing_order = (
            self.db.execute(
                select(SalesOrder).where(
                    SalesOrder.order_ref == order_ref,
                    SalesOrder.deleted_at.is_(None),
                )
            )
            .scalars()
            .first()
        )

        if existing_order:
            # Update existing order
            return existing_order, False

        # Get or create channel
        channel = self._get_or_create_shopify_channel()

        # Get or create customer
        customer_data = shopify_order.get("customer", {})
        customer = self._get_or_create_customer(customer_data)

        # Parse order date
        created_at = shopify_order.get("created_at")
        if created_at:
            order_date = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            order_date = datetime.utcnow()

        # Create sales order
        order = SalesOrder(
            id=str(uuid4()),
            customer_id=customer.id,
            channel_id=channel.id,
            order_ref=order_ref,
            order_date=order_date,
            status=SalesOrderStatus.CONFIRMED.value,
            source=SalesOrderSource.API.value,
            total_ex_gst=Decimal("0"),
            total_inc_gst=Decimal("0"),
        )

        self.db.add(order)
        self.db.flush()

        # Process line items
        line_items = shopify_order.get("line_items", [])
        sequence = 1
        total_ex_gst = Decimal("0")
        total_inc_gst = Decimal("0")

        for item in line_items:
            variant_id = str(item.get("variant_id", ""))
            sku = item.get("sku", "")
            quantity = Decimal(str(item.get("quantity", 0)))
            price = Decimal(str(item.get("price", "0")))

            # Find product
            product = None
            if sku:
                product = self._find_product_by_sku(sku)
            if not product and variant_id:
                product = self._find_product_by_variant_id(variant_id)

            if not product:
                # Skip items we can't match
                continue

            # Calculate prices (Shopify prices are typically inc tax)
            # For now, assume 10% GST
            tax_rate = Decimal("10.0")
            unit_price_inc_gst = price
            unit_price_ex_gst = unit_price_inc_gst / (1 + tax_rate / 100)

            # Calculate line totals
            line_total_ex_gst = unit_price_ex_gst * quantity
            line_total_inc_gst = unit_price_inc_gst * quantity

            # Calculate COGS
            # Convert quantity to kg (assuming 1 unit = 1 kg for now, adjust if needed)
            qty_kg = quantity
            cogs_per_unit, cogs_total = self.calculate_cogs(product.id, qty_kg)

            # Create order line
            order_line = SalesOrderLine(
                id=str(uuid4()),
                order_id=order.id,
                product_id=product.id,
                qty=qty_kg,
                uom="unit",
                unit_price_ex_gst=unit_price_ex_gst,
                unit_price_inc_gst=unit_price_inc_gst,
                tax_rate=tax_rate,
                line_total_ex_gst=line_total_ex_gst,
                line_total_inc_gst=line_total_inc_gst,
                sequence=sequence,
            )

            # Add COGS fields if they exist (will be added in migration)
            if hasattr(order_line, "cogs_per_unit"):
                order_line.cogs_per_unit = cogs_per_unit
            if hasattr(order_line, "cogs_total"):
                order_line.cogs_total = cogs_total

            self.db.add(order_line)

            total_ex_gst += line_total_ex_gst
            total_inc_gst += line_total_inc_gst
            sequence += 1

        # Update order totals
        order.total_ex_gst = total_ex_gst
        order.total_inc_gst = total_inc_gst

        self.db.flush()

        return order, True

    def import_historical_orders(
        self,
        since_date: Optional[datetime] = None,
        until_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        Import all historical orders from Shopify.

        Args:
            since_date: Start date for import (optional, defaults to all time)
            until_date: End date for import (optional)

        Returns:
            Summary dictionary with import results
        """
        created_count = 0
        updated_count = 0
        error_count = 0
        errors: List[str] = []

        # Format dates for Shopify API
        created_at_min = None
        if since_date:
            created_at_min = since_date.isoformat() + "Z"

        created_at_max = None
        if until_date:
            created_at_max = until_date.isoformat() + "Z"

        # Fetch orders with pagination
        since_id = None
        has_more = True

        while has_more:
            result = self.client.get_orders(
                created_at_min=created_at_min,
                created_at_max=created_at_max,
                since_id=since_id,
            )

            if not result.get("ok"):
                error_count += 1
                errors.append(f"Failed to fetch orders: {result.get('error')}")
                break

            orders = result.get("orders", [])
            if not orders:
                break

            # Process each order
            for shopify_order in orders:
                try:
                    order, created = self.import_order(shopify_order)
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    error_count += 1
                    order_id = shopify_order.get("id", "unknown")
                    errors.append(f"Failed to import order {order_id}: {str(e)}")

            # Check if there are more orders
            has_more = result.get("has_next", False)
            if orders:
                # Use the last order ID for pagination
                since_id = str(orders[-1].get("id"))

            self.db.commit()

        return {
            "ok": True,
            "created": created_count,
            "updated": updated_count,
            "errors": error_count,
            "error_details": errors,
        }

    def import_orders_since(
        self, last_order_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Import orders since the last imported order (incremental sync).

        Args:
            last_order_id: Last imported Shopify order ID (optional)

        Returns:
            Summary dictionary with import results
        """
        created_count = 0
        updated_count = 0
        error_count = 0
        errors: List[str] = []
        last_imported_id = last_order_id

        # Fetch orders with pagination
        since_id = last_order_id
        has_more = True

        while has_more:
            result = self.client.get_orders(since_id=since_id)

            if not result.get("ok"):
                error_count += 1
                errors.append(f"Failed to fetch orders: {result.get('error')}")
                break

            orders = result.get("orders", [])
            if not orders:
                break

            # Process each order
            for shopify_order in orders:
                try:
                    order, created = self.import_order(shopify_order)
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

                    # Track last imported ID
                    shopify_id = str(shopify_order.get("id"))
                    if not last_imported_id or int(shopify_id) > int(last_imported_id):
                        last_imported_id = shopify_id
                except Exception as e:
                    error_count += 1
                    order_id = shopify_order.get("id", "unknown")
                    errors.append(f"Failed to import order {order_id}: {str(e)}")

            # Check if there are more orders
            has_more = result.get("has_next", False)
            if orders:
                # Use the last order ID for pagination
                since_id = str(orders[-1].get("id"))

            self.db.commit()

        return {
            "ok": True,
            "created": created_count,
            "updated": updated_count,
            "errors": error_count,
            "error_details": errors,
            "last_order_id": last_imported_id,
        }

    def import_order_by_id(self, order_id: str) -> Dict[str, Any]:
        """
        Import a single order by Shopify order ID.

        Args:
            order_id: Shopify order ID

        Returns:
            Result dictionary
        """
        order_data = self.client.get_order_by_id(order_id)

        if not order_data:
            return {"ok": False, "error": f"Order {order_id} not found in Shopify"}

        try:
            order, created = self.import_order(order_data)
            self.db.commit()

            return {
                "ok": True,
                "order_id": order.id,
                "created": created,
                "shopify_order_id": order_id,
            }
        except Exception as e:
            self.db.rollback()
            return {"ok": False, "error": str(e)}
