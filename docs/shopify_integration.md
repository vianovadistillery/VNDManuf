# Shopify Integration (VND ⇄ Shopify)

**Flows**
- VND → Shopify: On production completion, stocktake, manual adjustment, or assembly/disassembly → compute `available_to_sell` → push to Shopify variant/location.
- Shopify → VND: Webhooks `orders/create`, `fulfillments/create`, `orders/cancelled`, `refunds/create` update reservations/commits and trigger pushes.

**Key tables**
- `assemblies` — parent↔child ratios (e.g., 1 CTN = 24 CAN), optional `loss_factor`.
- `product_channel_links` — product to Shopify variant/location mapping.
- `inventory_reservations` — optional gap handling between order and fulfilment.

**Security**
- Verify webhook HMAC.

**Reconciliation**
- Hourly job: compare VND `available_to_sell` vs Shopify; push corrections.

> NOTE: `app/adapters/shopify_client.py` is stubbed. Implement real inventory adjustments (GraphQL `inventoryAdjustQuantity`) and store `inventory_item_id` mapping as needed.
