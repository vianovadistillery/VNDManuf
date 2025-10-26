from fastapi import APIRouter, Request, Depends
# from app.adapters.db import get_db
# from sqlalchemy.orm import Session
from app.adapters.shopify_hmac import verify_webhook_hmac
# from app.services.shopify_sync import ShopifySyncService

router = APIRouter(prefix="/shopify", tags=["shopify"])

def _read_body_bytes(request: Request):
    return request._body if hasattr(request, "_body") else None

@router.post("/webhooks/orders_create")
async def orders_create(request: Request, x_shopify_hmac_sha256: str):
    raw = await request.body()
    # verify_webhook_hmac(raw, x_shopify_hmac_sha256, secret=<your_webhook_secret>)
    # db: Session = Depends(get_db)
    # svc = ShopifySyncService(db)
    # payload = await request.json()
    # return svc.apply_shopify_order(payload)
    return {"ok": True, "note": "orders_create stub"}

@router.post("/webhooks/fulfillments_create")
async def fulfillments_create(request: Request, x_shopify_hmac_sha256: str):
    raw = await request.body()
    # verify_webhook_hmac(raw, x_shopify_hmac_sha256, secret=<your_webhook_secret>)
    # svc.apply_shopify_fulfillment(await request.json())
    return {"ok": True, "note": "fulfillments_create stub"}

@router.post("/webhooks/orders_cancelled")
async def orders_cancelled(request: Request, x_shopify_hmac_sha256: str):
    raw = await request.body()
    # verify_webhook_hmac(raw, x_shopify_hmac_sha256, secret=<your_webhook_secret>)
    return {"ok": True, "note": "orders_cancelled stub"}

@router.post("/webhooks/refunds_create")
async def refunds_create(request: Request, x_shopify_hmac_sha256: str):
    raw = await request.body()
    # verify_webhook_hmac(raw, x_shopify_hmac_sha256, secret=<your_webhook_secret>)
    return {"ok": True, "note": "refunds_create stub"}

@router.post("/sync/push/{product_id}")
def push_one(product_id: str):
    # db: Session = Depends(get_db)
    # svc = ShopifySyncService(db)
    # return svc.push_inventory(product_id)
    return {"ok": True, "note": f"push stub for {product_id}"}

@router.post("/sync/push-all")
def push_all():
    # db: Session = Depends(get_db)
    # svc = ShopifySyncService(db)
    # return svc.reconcile_all()
    return {"ok": True, "note": "push-all stub"}

