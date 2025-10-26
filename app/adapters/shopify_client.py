import time
from typing import Optional, Dict, Any
import requests
from app.settings import settings

class ShopifyClient:
    def __init__(self, store: str | None = None, token: str | None = None):
        self.store = store or str(settings.shopify.store).rstrip("/")
        self.token = token or settings.shopify.access_token

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def set_inventory_level(self, variant_id: str, location_id: str, available: int) -> Dict[str, Any]:
        """
        Minimal REST call using InventoryLevel endpoint via InventoryItem mapping.
        In practice you must map variant -> inventory_item_id first (once) and store it.
        This stub assumes you've already stored that mapping as variant_id or you switch to GraphQL.
        """
        # Placeholder: you likely want to use GraphQL mutation inventoryAdjustQuantity
        url = f"{self.store}/admin/api/2024-10/variants/{variant_id}.json"
        # NOTE: This endpoint doesn't set inventory directly – you will implement the real call in your project.
        # This stub demonstrates structure; replace with inventoryAdjustQuantity GraphQL mutation as needed.
        return {"ok": True, "note": "stubbed set_inventory_level; implement GraphQL inventoryAdjustQuantity"}

    def backoff(self, attempt: int):
        time.sleep(min(1.0 * attempt, 10.0))

