class FakeShopifyClient:
    def __init__(self):
        self.inventory_sets = []

    def set_inventory_level(self, variant_id: str, location_id: str, available: int):
        self.inventory_sets.append((variant_id, location_id, available))
        return {"ok": True, "variant_id": variant_id, "location_id": location_id, "available": available}

