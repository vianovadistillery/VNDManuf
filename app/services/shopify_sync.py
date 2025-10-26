from typing import Dict, Any, List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.adapters.shopify_client import ShopifyClient
from app.adapters.db.models_assemblies_shopify import ProductChannelLink, InventoryReservation
from app.settings import settings

# from app.services.inventory import available_to_sell, commit_reservation, release_reservation, decrement_fifo

class ShopifySyncService:
    def __init__(self, db: Session, client: Optional[ShopifyClient] = None):
        self.db = db
        self.client = client or ShopifyClient()

    def push_inventory(self, product_id: str) -> Dict[str, Any]:
        """
        Compute available_to_sell(product_id) in SELLABLE UNITS and push to Shopify variant/location.
        """
        # qty = available_to_sell(self.db, product_id)  # implement in your inventory service
        link = self.db.query(ProductChannelLink).filter_by(product_id=product_id, channel="shopify").first()
        if not link or not link.shopify_variant_id:
            return {"ok": False, "error": "no_shopify_mapping"}
        location_id = link.shopify_location_id or settings.shopify.location_id
        if not location_id:
            return {"ok": False, "error": "no_location_id"}
        # result = self.client.set_inventory_level(link.shopify_variant_id, location_id, int(qty))
        result = self.client.set_inventory_level(link.shopify_variant_id, location_id, 0)  # stub
        return {"ok": True, "result": result}

    def apply_shopify_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle orders/create webhook:
        - create ACTIVE reservations per line item
        """
        # TODO: map variant_id -> product_id; create reservations
        return {"ok": True, "note": "stub reservations created"}

    def apply_shopify_fulfillment(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle fulfillments/create webhook:
        - convert reservations to committed; decrement FIFO; push inventory
        """
        # TODO: commit reservations and push
        return {"ok": True, "note": "stub fulfillment processed"}

    def apply_shopify_cancel(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        orders/cancelled: release reservations
        """
        # TODO: release reservations
        return {"ok": True, "note": "stub cancel processed"}

    def apply_shopify_refund(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        refunds/create: if returned to stock, increment and push
        """
        # TODO: restock logic
        return {"ok": True, "note": "stub refund processed"}

    def reconcile_all(self) -> Dict[str, Any]:
        """
        Compare VND available_to_sell vs Shopify per mapped product and fix drift (push).
        """
        mapped = self.db.query(ProductChannelLink).filter_by(channel="shopify").all()
        results = []
        for link in mapped:
            results.append(self.push_inventory(link.product_id))
        return {"ok": True, "count": len(results), "results": results}

