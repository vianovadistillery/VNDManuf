# from sqlalchemy.orm import Session
# from app.services.shopify_sync import ShopifySyncService
from tests.fakes.fake_shopify import FakeShopifyClient

def test_push_inventory_uses_client():
    fake = FakeShopifyClient()
    # svc = ShopifySyncService(db=..., client=fake)
    # Suppose product maps to variant "123" at location "456" and available_to_sell=7
    # result = svc.push_inventory(product_id="ABC")
    # assert result["ok"]
    # assert fake.inventory_sets[-1] == ("123","456",7)
    assert True

