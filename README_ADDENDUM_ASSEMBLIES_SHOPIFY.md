# Assemblies + Shopify Sync Addendum

## Wire the routers
In `app/api/main.py` (or equivalent), add:
```python
from app.api import assemblies, shopify
app.include_router(assemblies.router)
app.include_router(shopify.router)

Run migration
alembic upgrade head

Implement internals

Replace TODOs:

Inventory math: canonical units, FIFO consume/add, available_to_sell(product_id).

Shopify client: use GraphQL to adjust inventory; persist variant_id & inventory_item_id.

Local testing

Use tests/ to expand unit tests.

Manually hit:

POST /assemblies/assemble

POST /assemblies/disassemble

POST /shopify/sync/push/{product_id}

Webhooks

Configure Shopify webhooks to point at:

/shopify/webhooks/orders_create

/shopify/webhooks/fulfillments_create

/shopify/webhooks/orders_cancelled

/shopify/webhooks/refunds_create

Remember to verify HMAC in production.


---

**END OF CURSOR PROMPT**
