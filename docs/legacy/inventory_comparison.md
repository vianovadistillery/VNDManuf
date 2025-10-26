# Legacy ACSTK vs Modern Inventory Schema Comparison

## Overview
The legacy `acstk` file stores aggregated stock information per product. The modern schema uses lot-based tracking with detailed transactions. This document compares the two approaches.

## Field-by-Field Comparison

### ✅ Fully Covered Fields

| Legacy Field | Type | Size | Modern Schema | How It's Covered |
|-------------|------|------|--------------|------------------|
| `soh` (Stock on Hand) | INTEGER | 2 | `inventory_lots.quantity_kg` | Sum across all active lots for a product |
| `purcost` (Purchase cost) | SINGLE | 4 | `inventory_lots.unit_cost` | Stored per lot (supports FIFO costing) |
| `date` (Last transaction) | STRING * 8 | 8 | `inventory_txns.created_at` | Most recent transaction timestamp |

### 📊 Calculated/Aggregated Fields

| Legacy Field | Type | Modern Schema | Calculation Method |
|-------------|------|--------------|-------------------|
| `sohv` (Stock on Hand Value) | SINGLE | Not stored | `SUM(lot.quantity_kg * lot.unit_cost)` |
| `cogs` (Cost of goods sold) | SINGLE | Not stored | `SUM(issue_txn.quantity_kg * issue_txn.unit_cost)` |
| `gpr` (Gross profit ratio) | SINGLE | Not stored | `(sales - cogs) / sales * 100` |

### 🔄 Requires Aggregation from Related Tables

| Legacy Field | Type | Modern Schema | How to Get It |
|-------------|------|--------------|---------------|
| `sip` (Stock in Progress) | INTEGER | Not stored | Query `work_orders` with status = 'IN_PROGRESS', sum allocated quantities |
| `soo` (Stock on Order) | INTEGER | Not stored | Query `purchase_orders` with status NOT IN ('CANCELLED', 'RECEIVED'), sum `po_lines.quantity_kg` |
| `sold` (Quantity Sold) | INTEGER | Not stored | Query `so_lines` from completed orders, sum shipped quantities |

## Schema Differences

### Legacy Approach (Flat/Denormalized)
- **Single record per product** with aggregated stock metrics
- Stock tracked as a single integer
- No lot tracking
- No transaction history
- **Pros**: Simple queries, fast lookups
- **Cons**: No audit trail, limited FIFO costing

### Modern Approach (Normalized/Lot-Based)
- **Lot-based inventory** with full transaction history
- Stock tracked per lot with quantities
- Complete audit trail via `inventory_txns`
- Supports FIFO costing and lot traceability
- **Pros**: Better data integrity, audit trail, multi-lot support
- **Cons**: Requires aggregation queries for totals

## Coverage Assessment

### ✅ Sufficient Coverage

The modern schema **IS sufficient** to cover all legacy stock fields, but with important caveats:

1. **Direct Stock (soh)** ✅
   - Stored in `inventory_lots.quantity_kg`
   - Query: `SELECT SUM(quantity_kg) FROM inventory_lots WHERE product_id = ? AND is_active = TRUE`

2. **Stock Value (sohv)** ✅
   - Calculated from lots
   - Query: `SELECT SUM(quantity_kg * unit_cost) FROM inventory_lots WHERE product_id = ?`

3. **Purchase Cost (purcost)** ✅
   - Stored in `inventory_lots.unit_cost`
   - Also tracked in `inventory_txns.unit_cost` for historical tracking

4. **Last Transaction Date** ✅
   - Query: `SELECT MAX(created_at) FROM inventory_txns WHERE lot_id IN (SELECT id FROM inventory_lots WHERE product_id = ?)`

5. **Stock in Progress (sip)** ✅
   - Query work orders with status 'IN_PROGRESS'
   - Query: `SELECT SUM(allocated_quantity_kg) FROM work_order_lines WHERE work_order_id IN (SELECT id FROM work_orders WHERE status = 'IN_PROGRESS')`

6. **Stock on Order (soo)** ✅
   - Query purchase orders with pending status
   - Query: `SELECT SUM(quantity_kg) FROM po_lines WHERE purchase_order_id IN (SELECT id FROM purchase_orders WHERE status NOT IN ('CANCELLED', 'RECEIVED'))`

7. **Quantity Sold (sold)** ✅
   - Query from sales order lines or invoices
   - Query: `SELECT SUM(so_lines.quantity_kg) FROM so_lines JOIN sales_orders ON so_lines.sales_order_id = sales_orders.id WHERE sales_orders.status IN ('SHIPPED', 'INVOICED') AND so_lines.product_id = ?`

## Missing in Legacy Schema

The modern schema tracks information not present in legacy:

1. **Lot Codes** - Traceability for raw materials
2. **Expiration Dates** - For perishable products
3. **Transaction History** - Complete audit trail
4. **Reference Tracking** - Which PO, WO, or SO created each transaction

## Migration Implications

When migrating legacy data:

1. **Create a single lot** per product from `soh`
   ```python
   lot = InventoryLot(
       lot_code=f"LEGACY-{product.sku}",
       product_id=product.id,
       quantity_kg=legacy.soh,
       unit_cost=legacy.purcost
   )
   ```

2. **Create initial transaction** for historical data
   ```python
   txn = InventoryTxn(
       lot_id=lot.id,
       transaction_type="RECEIPT",
       quantity_kg=legacy.soh,
       unit_cost=legacy.purcost,
       reference_type="LEGACY_MIGRATION",
       notes=f"Migrated from legacy stock file"
   )
   ```

3. **Create purchase order** for stock on order (if applicable)
   ```python
   if legacy.soo > 0:
       po = PurchaseOrder(
           supplier_id=find_supplier(legacy.suplr),
           po_number=f"LEGACY-SOO-{legacy.search}",
           status="SENT"
       )
   ```

4. **Calculate COGS from sales** (if historical data exists)
   ```python
   # Query sales order lines
   # Apply FIFO to calculate COGS for each sale
   ```

## Recommendation

**The modern schema is MORE than sufficient** - it provides better tracking than the legacy system:

1. ✅ All legacy stock metrics can be calculated/aggregated
2. ✅ Provides audit trail and transaction history
3. ✅ Supports multi-lot tracking
4. ✅ Enables FIFO costing
5. ✅ Tracks stock commitments (sip, soo)
6. ✅ Supports expiration dates and lot traceability

**Trade-off**: Requires query aggregation instead of simple field reads, but this is a good trade-off for data integrity and functionality.

## SQL Views for Legacy Compatibility

If you need to maintain compatibility with legacy queries, create SQL views:

```sql
CREATE VIEW v_product_stock AS
SELECT 
    p.id as product_id,
    p.sku,
    p.name,
    COALESCE(SUM(l.quantity_kg), 0) as soh,
    COALESCE(SUM(l.quantity_kg * l.unit_cost), 0) as sohv,
    COALESCE(MAX(l.received_at), p.created_at) as last_transaction_date
FROM products p
LEFT JOIN inventory_lots l ON p.id = l.product_id AND l.is_active = TRUE
GROUP BY p.id, p.sku, p.name, p.created_at;
```

This provides legacy-compatible views while maintaining the normalized modern structure.

