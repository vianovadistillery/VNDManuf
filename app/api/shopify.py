from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.adapters.db import get_db
from app.adapters.shopify_hmac import verify_webhook_hmac
from app.services.shopify_sync import ShopifySyncService
from app.settings import settings

router = APIRouter(prefix="/shopify", tags=["shopify"])


async def _read_body_bytes(request: Request):
    body = await request.body()
    request._body_bytes = body
    return body


@router.post("/webhooks/orders_create")
async def orders_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Handle Shopify orders/create webhook.
    Creates inventory reservations for order line items.
    """
    raw = await request.body()

    # Verify HMAC signature
    if not verify_webhook_hmac(
        raw, x_shopify_hmac_sha256, settings.shopify.webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = await request.json()
    svc = ShopifySyncService(db)
    result = svc.apply_shopify_order(payload)

    return result


@router.post("/webhooks/fulfillments_create")
async def fulfillments_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Handle Shopify fulfillments/create webhook.
    Commits reservations and updates inventory.
    """
    raw = await request.body()

    # Verify HMAC signature
    if not verify_webhook_hmac(
        raw, x_shopify_hmac_sha256, settings.shopify.webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = await request.json()
    svc = ShopifySyncService(db)
    result = svc.apply_shopify_fulfillment(payload)

    return result


@router.post("/webhooks/orders_cancelled")
async def orders_cancelled(
    request: Request,
    x_shopify_hmac_sha256: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Handle Shopify orders/cancelled webhook.
    Releases inventory reservations.
    """
    raw = await request.body()

    # Verify HMAC signature
    if not verify_webhook_hmac(
        raw, x_shopify_hmac_sha256, settings.shopify.webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = await request.json()
    svc = ShopifySyncService(db)
    result = svc.apply_shopify_cancel(payload)

    return result


@router.post("/webhooks/refunds_create")
async def refunds_create(
    request: Request,
    x_shopify_hmac_sha256: str = Header(...),
    db: Session = Depends(get_db),
):
    """
    Handle Shopify refunds/create webhook.
    Handles inventory restocking if applicable.
    """
    raw = await request.body()

    # Verify HMAC signature
    if not verify_webhook_hmac(
        raw, x_shopify_hmac_sha256, settings.shopify.webhook_secret
    ):
        raise HTTPException(status_code=401, detail="Invalid HMAC signature")

    payload = await request.json()
    svc = ShopifySyncService(db)
    result = svc.apply_shopify_refund(payload)

    return result


@router.post("/sync/push/{product_id}")
def push_one(product_id: str, db: Session = Depends(get_db)):
    """
    Manually push inventory for a specific product to Shopify.
    """
    svc = ShopifySyncService(db)
    result = svc.push_inventory(product_id)
    return result


@router.post("/sync/push-all")
def push_all(db: Session = Depends(get_db)):
    """
    Manually reconcile and push all mapped products to Shopify.
    """
    svc = ShopifySyncService(db)
    result = svc.reconcile_all()
    return result
