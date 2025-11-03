# Assembly + Shopify Integration

This document describes the completed Assembly and Shopify integration features.

## Overview

The system now supports:
1. **Assembly Operations**: Assemble parent products from child components and disassemble them back
2. **Shopify Integration**: Sync inventory with Shopify, handle orders via webhooks, and manage reservations

## Assembly System

### Architecture

The assembly system is built on three core components:

1. **Assembly Model** (`app/adapters/db/models_assemblies_shopify.py`):
   - Defines parent-child product relationships
   - Supports configurable ratios and loss factors
   - Direction: `MAKE_FROM_CHILDREN` or `BREAK_INTO_CHILDREN`

2. **Assembly Service** (`app/services/assembly_service.py`):
   - `assemble()`: Consume child components via FIFO, produce parent product
   - `disassemble()`: Consume parent via FIFO, produce child components (with loss factor)
   - Automatic cost calculation based on consumed components

3. **Inventory Service Integration**:
   - Uses existing FIFO logic from `app/domain/rules.py`
   - Creates inventory transactions for audit trail
   - Maintains proper lot codes and timestamps

### API Endpoints

#### POST `/api/v1/assemblies/assemble`
Assemble a parent product from child components.

**Request:**
```json
{
  "parent_product_id": "uuid",
  "qty": 10.0,
  "reason": "ORDER_FULFILLMENT"
}
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "consumed": [
      {
        "child_product_id": "uuid",
        "ratio": 2.0,
        "loss_factor": 0.05,
        "qty_consumed": 21.0,
        "cost": 210.0,
        "issues": [...]
      }
    ],
    "produced": {
      "product_id": "uuid",
      "quantity_kg": 10.0,
      "unit_cost": 21.0,
      "total_cost": 210.0,
      "lot_id": "uuid",
      "lot_code": "ASSM-20250127-123456"
    }
  }
}
```

#### POST `/api/v1/assemblies/disassemble`
Disassemble a parent product into child components.

**Request:**
```json
{
  "parent_product_id": "uuid",
  "qty": 5.0,
  "reason": "INVENTORY_ADJUSTMENT"
}
```

### Database Schema

```sql
CREATE TABLE assemblies (
    id VARCHAR(36) PRIMARY KEY,
    parent_product_id VARCHAR(36) NOT NULL,
    child_product_id VARCHAR(36) NOT NULL,
    ratio NUMERIC(18,6) NOT NULL DEFAULT 1,
    direction VARCHAR(32) NOT NULL DEFAULT 'MAKE_FROM_CHILDREN',
    loss_factor NUMERIC(6,4) NOT NULL DEFAULT 0
);
```

## Shopify Integration

### Architecture

The Shopify integration provides seamless inventory synchronization and order management:

1. **ProductChannelLink** (`product_channel_links` table):
   - Maps products to Shopify variants and locations
   - Stores Shopify IDs for efficient lookups

2. **Inventory Reservations** (`inventory_reservations` table):
   - Prevents double-booking during order→fulfillment gap
   - Tracks order lifecycle: ACTIVE → COMMITTED or RELEASED

3. **Shopify Client** (`app/adapters/shopify_client.py`):
   - REST API wrapper for Shopify inventory operations
   - Supports getting/setting inventory levels

4. **Shopify Sync Service** (`app/services/shopify_sync.py`):
   - Handles all Shopify-related business logic
   - Webhook processing for orders, fulfillments, cancellations

### Webhook Endpoints

All webhooks require HMAC signature verification using `X-Shopify-Hmac-Sha256` header.

#### POST `/api/v1/shopify/webhooks/orders_create`
Creates inventory reservations when an order is placed in Shopify.

**Flow:**
1. Parse order line items
2. Map Shopify variant IDs to internal product IDs
3. Create ACTIVE reservations for each line item
4. Return reservation IDs

#### POST `/api/v1/shopify/webhooks/fulfillments_create`
Commits reservations and updates inventory when order is fulfilled.

**Flow:**
1. Find all ACTIVE reservations for the order
2. Commit each reservation (consumes via FIFO)
3. Push updated inventory to Shopify for affected products

#### POST `/api/v1/shopify/webhooks/orders_cancelled`
Releases reservations when an order is cancelled.

**Flow:**
1. Find all ACTIVE reservations for the order
2. Release each reservation (status → RELEASED)
3. Make inventory available again

#### POST `/api/v1/shopify/webhooks/refunds_create`
Handles refund processing (stub implementation - to be completed).

### Manual Operations

#### POST `/api/v1/shopify/sync/push/{product_id}`
Manually push inventory for a specific product to Shopify.

#### POST `/api/v1/shopify/sync/push-all`
Reconcile and push all mapped products to Shopify.

### Database Schema

```sql
CREATE TABLE product_channel_links (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    channel VARCHAR(32) NOT NULL DEFAULT 'shopify',
    shopify_product_id VARCHAR(64),
    shopify_variant_id VARCHAR(64),
    shopify_location_id VARCHAR(64),
    UNIQUE(product_id, channel)
);

CREATE TABLE inventory_reservations (
    id VARCHAR(36) PRIMARY KEY,
    product_id VARCHAR(36) NOT NULL,
    qty_canonical NUMERIC(18,6) NOT NULL,
    source VARCHAR(16) NOT NULL,  -- 'shopify'|'internal'
    reference_id VARCHAR(128),     -- e.g., Shopify order ID
    status VARCHAR(16) NOT NULL DEFAULT 'ACTIVE',  -- ACTIVE|RELEASED|COMMITTED
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
);
```

## Usage Examples

### 1. Setting Up Assembly

```python
from app.adapters.db import get_db
from app.adapters.db.models import Product
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection

db = next(get_db())

# Create parent product
parent = Product(sku="PAINT-1L", name="1L Paint", base_unit="KG")
child = Product(sku="BASE-1L", name="Base 1L", base_unit="KG")
db.add_all([parent, child])
db.flush()

# Define assembly: 1L paint needs 0.9L base + 0.1L color
assembly = Assembly(
    parent_product_id=parent.id,
    child_product_id=child.id,
    ratio=Decimal("0.9"),  # 0.9kg base per 1kg paint
    direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
    loss_factor=Decimal("0.05")  # 5% loss during mixing
)
db.add(assembly)
db.commit()
```

### 2. Assembling Products

```python
from app.services.assembly_service import AssemblyService

svc = AssemblyService(db)
result = svc.assemble(parent.id, Decimal("100.0"), "ORDER_FULFILLMENT")
db.commit()

print(f"Produced {result['produced']['quantity_kg']} kg")
print(f"Consumed {result['consumed'][0]['qty_consumed']} kg child")
```

### 3. Setting Up Shopify Mapping

```python
from app.adapters.db.models_assemblies_shopify import ProductChannelLink

link = ProductChannelLink(
    product_id=parent.id,
    channel="shopify",
    shopify_product_id="12345678",
    shopify_variant_id="87654321",
    shopify_location_id="11223344"
)
db.add(link)
db.commit()
```

### 4. Pushing Inventory to Shopify

```python
from app.services.shopify_sync import ShopifySyncService

svc = ShopifySyncService(db)
result = svc.push_inventory(parent.id)
print(result)  # {"ok": True, "response": {...}}
```

## Testing

Comprehensive test coverage is provided in:
- `tests/test_assembly_service.py`: Assembly operations (assemble, disassemble, multiple children, insufficient stock)
- `tests/test_shopify_sync.py`: Inventory reservations, Shopify webhooks

Run tests:
```bash
pytest tests/test_assembly_service.py -v
pytest tests/test_shopify_sync.py -v
```

## Configuration

Shopify settings are configured via environment variables (see `app/settings.py`):

```bash
SHOPIFY_STORE=https://yourstore.myshopify.com
SHOPIFY_ACCESS_TOKEN=shpat_xxx
SHOPIFY_LOCATION_ID=11223344
SHOPIFY_WEBHOOK_SECRET=your_webhook_secret
```

## Migration

The database migration has already been applied. To check status:

```bash
alembic current
```

To apply manually (if needed):
```bash
alembic upgrade head
```

## Future Enhancements

1. **Partial Refunds**: Complete implementation of `apply_shopify_refund()` with inventory restocking
2. **Batch Assembly**: Support for batch-level assembly tracking
3. **Pack Unit Conversion**: Automatic conversion between internal units (kg) and Shopify sellable units
4. **Multi-Location Support**: Enhanced handling for multi-location Shopify stores
5. **GraphQL API**: Consider migrating from REST to GraphQL for better performance
