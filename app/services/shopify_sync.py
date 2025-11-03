from decimal import Decimal
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.adapters.db.models_assemblies_shopify import (
    InventoryReservation,
    ProductChannelLink,
)
from app.adapters.shopify_client import ShopifyClient
from app.services.inventory import InventoryService
from app.settings import settings


class ShopifySyncService:
    def __init__(self, db: Session, client: Optional[ShopifyClient] = None):
        self.db = db
        self.client = client or ShopifyClient()
        self.inventory = InventoryService(db)

    def push_inventory(self, product_id: str) -> Dict[str, Any]:
        """
        Compute available_to_sell(product_id) in SELLABLE UNITS and push to Shopify variant/location.
        Returns available qty in whole units (assume product pack=1 for now).
        """
        # Get channel link
        link = (
            self.db.query(ProductChannelLink)
            .filter_by(product_id=product_id, channel="shopify")
            .first()
        )

        if not link or not link.shopify_variant_id:
            return {"ok": False, "error": "no_shopify_mapping"}

        location_id = link.shopify_location_id or settings.shopify.location_id
        if not location_id:
            return {"ok": False, "error": "no_location_id"}

        # Get available quantity in canonical units (kg)
        available_kg = self.inventory.available_to_sell(product_id)

        # Convert to sellable units (assume 1kg = 1 unit for now)
        # TODO: Add pack unit conversion if needed
        sellable_qty = int(available_kg)

        # Get inventory item ID from variant ID
        inventory_item_id = self.client.get_inventory_item_id(link.shopify_variant_id)
        if not inventory_item_id:
            return {"ok": False, "error": "failed_to_get_inventory_item_id"}

        # Set inventory level
        result = self.client.set_inventory_level(
            inventory_item_id=inventory_item_id,
            location_id=location_id,
            available=sellable_qty,
        )

        return result

    def apply_shopify_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle orders/create webhook:
        - Create ACTIVE reservations per line item
        """
        order_id = payload.get("id")
        line_items = payload.get("line_items", [])

        created_reservations = []

        for item in line_items:
            variant_id = item.get("variant_id")
            quantity = int(item.get("quantity", 0))

            if not variant_id or quantity <= 0:
                continue

            # Find product by shopify_variant_id
            link = (
                self.db.query(ProductChannelLink)
                .filter_by(shopify_variant_id=str(variant_id), channel="shopify")
                .first()
            )

            if not link:
                continue

            # Convert quantity to canonical units (kg)
            qty_kg = Decimal(quantity)

            # Create reservation
            try:
                reservation = self.inventory.reserve_inventory(
                    product_id=link.product_id,
                    qty_kg=qty_kg,
                    source="shopify",
                    reference_id=str(order_id),
                )
                self.db.commit()
                created_reservations.append(
                    {
                        "product_id": link.product_id,
                        "quantity": quantity,
                        "reservation_id": reservation.id,
                    }
                )
            except ValueError as e:
                # Already reserved or other error
                self.db.rollback()
                return {"ok": False, "error": str(e)}

        return {"ok": True, "order_id": order_id, "reservations": created_reservations}

    def apply_shopify_fulfillment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle fulfillments/create webhook:
        - Convert reservations to committed; decrement FIFO; push inventory
        """
        order_id = payload.get("order_id")

        # Find all active reservations for this order
        reservations = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.reference_id == str(order_id),
                InventoryReservation.source == "shopify",
                InventoryReservation.status == "ACTIVE",
            )
            .all()
        )

        committed_count = 0

        for reservation in reservations:
            try:
                # Commit the reservation (consumes via FIFO)
                self.inventory.commit_reservation(reservation.id)
                committed_count += 1
            except ValueError as e:
                self.db.rollback()
                return {
                    "ok": False,
                    "error": f"Failed to commit reservation {reservation.id}: {str(e)}",
                }

        self.db.commit()

        # Push updated inventory for all affected products
        product_ids = set(r.product_id for r in reservations)
        push_results = []

        for product_id in product_ids:
            result = self.push_inventory(product_id)
            push_results.append({product_id: result})

        return {
            "ok": True,
            "order_id": order_id,
            "committed_reservations": committed_count,
            "inventory_pushed": push_results,
        }

    def apply_shopify_cancel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        orders/cancelled: release reservations
        """
        order_id = payload.get("id")

        # Find all active reservations for this order
        reservations = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.reference_id == str(order_id),
                InventoryReservation.source == "shopify",
                InventoryReservation.status == "ACTIVE",
            )
            .all()
        )

        released_count = 0

        for reservation in reservations:
            try:
                self.inventory.release_reservation(reservation.id)
                released_count += 1
            except ValueError as e:
                return {
                    "ok": False,
                    "error": f"Failed to release reservation {reservation.id}: {str(e)}",
                }

        self.db.commit()

        return {
            "ok": True,
            "order_id": order_id,
            "released_reservations": released_count,
        }

    def apply_shopify_refund(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        refunds/create: if returned to stock, increment and push
        Note: This is simplified - production would need to handle partial refunds
        """
        order_id = payload.get("order_id")

        # For now, just log that a refund occurred
        # Production implementation would:
        # 1. Check if inventory is being restocked
        # 2. Create new lots with returned quantities
        # 3. Push updated inventory

        return {
            "ok": True,
            "order_id": order_id,
            "note": "Refund logged - restocking logic to be implemented",
        }

    def reconcile_all(self) -> Dict[str, Any]:
        """
        Compare VND available_to_sell vs Shopify per mapped product and fix drift (push).
        """
        mapped = self.db.query(ProductChannelLink).filter_by(channel="shopify").all()
        results = []

        for link in mapped:
            result = self.push_inventory(link.product_id)
            results.append({"product_id": link.product_id, "result": result})

        successful = sum(1 for r in results if r["result"].get("ok"))

        return {
            "ok": True,
            "total_mapped": len(mapped),
            "successful": successful,
            "results": results,
        }
