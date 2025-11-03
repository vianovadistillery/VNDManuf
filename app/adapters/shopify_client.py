import time
from typing import Any, Dict, Optional

import requests

from app.settings import settings


class ShopifyClient:
    def __init__(self, store: str | None = None, token: str | None = None):
        self.store = store or str(settings.shopify.store).rstrip("/")
        self.token = token or settings.shopify.access_token
        self.base_url = f"{self.store}/admin/api/2024-10"

    def _headers(self) -> Dict[str, str]:
        return {
            "X-Shopify-Access-Token": self.token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def get_inventory_item_id(self, variant_id: str) -> Optional[str]:
        """
        Get inventory item ID from variant ID.
        This mapping needs to be stored locally for performance.
        """
        url = f"{self.base_url}/variants/{variant_id}.json"
        response = requests.get(url, headers=self._headers())

        if response.status_code == 200:
            variant_data = response.json()
            return variant_data.get("variant", {}).get("inventory_item_id")
        return None

    def set_inventory_level(
        self, inventory_item_id: str, location_id: str, available: int
    ) -> Dict[str, Any]:
        """
        Set inventory level using GraphQL mutation.
        This is the recommended way to update inventory in Shopify.
        """
        # For REST API (simpler, but limited)
        # First, get the inventory_level_id
        url = f"{self.base_url}/inventory_levels/set.json"
        payload = {
            "location_id": location_id,
            "inventory_item_id": inventory_item_id,
            "available": available,
        }

        response = requests.post(url, headers=self._headers(), json=payload)

        if response.status_code in [200, 201]:
            return {"ok": True, "response": response.json()}
        else:
            return {
                "ok": False,
                "error": response.text,
                "status_code": response.status_code,
            }

    def get_inventory_level(
        self, inventory_item_id: str, location_id: str
    ) -> Optional[int]:
        """
        Get current inventory level.
        """
        url = f"{self.base_url}/inventory_levels.json"
        params = {"inventory_item_ids": inventory_item_id, "location_ids": location_id}

        response = requests.get(url, headers=self._headers(), params=params)

        if response.status_code == 200:
            data = response.json()
            levels = data.get("inventory_levels", [])
            if levels:
                return levels[0].get("available")
        return None

    def backoff(self, attempt: int):
        """Exponential backoff for retries."""
        time.sleep(min(1.0 * (2**attempt), 10.0))
