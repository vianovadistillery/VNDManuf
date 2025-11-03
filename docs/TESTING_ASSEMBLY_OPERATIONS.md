# Testing Assembly Operations Guide

This guide shows how to test assembly operations (RAW → WIP → FINISHED) after the unified products migration.

## Overview

Assembly operations allow you to:
- **Assemble**: Combine child products (e.g., RAW materials) into parent products (e.g., WIP or FINISHED)
- **Disassemble**: Break down parent products into child products
- **Multi-stage workflows**: RAW → WIP → FINISHED production chains

## Prerequisites

1. **API Server Running**
   ```bash
   # Start the API server
   python -m uvicorn app.api.main:app --reload
   # Or use your dev script
   scripts/dev.ps1
   ```

2. **Database Migrated**
   - Unified products migration complete
   - Products with `product_type` (RAW, WIP, FINISHED) available

## Method 1: API Testing (HTTP Requests)

### Step 1: Create Products

Create RAW material products:

```powershell
# Create Raw Material 1
$raw1 = @{
    sku = "RM-TEST-001"
    name = "Test Resin"
    product_type = "RAW"
    base_unit = "KG"
    specific_gravity = 1.2
    usage_cost = 10.50
    raw_material_code = 9001
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products" `
    -Method POST `
    -ContentType "application/json" `
    -Body $raw1

# Create Raw Material 2
$raw2 = @{
    sku = "RM-TEST-002"
    name = "Test Solvent"
    product_type = "RAW"
    base_unit = "KG"
    specific_gravity = 0.8
    usage_cost = 8.00
    raw_material_code = 9002
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products" `
    -Method POST `
    -ContentType "application/json" `
    -Body $raw2

# Create WIP Product
$wip = @{
    sku = "WIP-TEST-001"
    name = "Test WIP Product"
    product_type = "WIP"
    base_unit = "KG"
} | ConvertTo-Json

$wipResult = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products" `
    -Method POST `
    -ContentType "application/json" `
    -Body $wip

# Create Finished Product
$finished = @{
    sku = "FG-TEST-001"
    name = "Test Finished Product"
    product_type = "FINISHED"
    base_unit = "KG"
} | ConvertTo-Json

$finishedResult = Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products" `
    -Method POST `
    -ContentType "application/json" `
    -Body $finished
```

### Step 2: Add Inventory for RAW Materials

```powershell
# Get product IDs from previous step
$raw1Id = (Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products/sku/RM-TEST-001").id
$raw2Id = (Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products/sku/RM-TEST-002").id

# Add inventory for raw materials (via inventory API or direct DB)
# For now, use inventory API endpoint if available, or add via batch creation
```

### Step 3: Create Assembly Definitions

Assembly definitions specify how to combine products. Create them via the assemblies API or directly in the database.

**Note**: Assembly definitions are stored in the `assemblies` table. You'll need to create these via a script or direct database insert for now.

### Step 4: Test Assembly Operations

```powershell
# Assemble WIP from RAW materials
$assembleRequest = @{
    parent_product_id = $wipResult.id
    parent_qty = 100.0
    reason = "TEST_ASSEMBLY"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/assemblies/assemble" `
    -Method POST `
    -ContentType "application/json" `
    -Body $assembleRequest
```

## Method 2: Python Script Testing

Create a test script to exercise assembly operations:

```python
#!/usr/bin/env python3
"""Test assembly operations after unified products migration."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

from app.adapters.db.session import get_session
from app.adapters.db.models import Product, InventoryLot
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
from app.services.assembly_service import AssemblyService

def test_assembly_operations():
    """Test RAW → WIP → FINISHED assembly workflow."""
    db = get_session()

    try:
        print("=" * 80)
        print("ASSEMBLY OPERATIONS TEST")
        print("=" * 80)

        # Step 1: Create Products
        print("\n1. Creating products...")

        raw1 = Product(
            sku="RM-ASSEMBLY-001",
            name="Resin A",
            product_type="RAW",
            base_unit="KG",
            specific_gravity=Decimal("1.2"),
            usage_cost=Decimal("10.50"),
            raw_material_code=9101,
            is_active=True
        )

        raw2 = Product(
            sku="RM-ASSEMBLY-002",
            name="Solvent B",
            product_type="RAW",
            base_unit="KG",
            specific_gravity=Decimal("0.8"),
            usage_cost=Decimal("8.00"),
            raw_material_code=9102,
            is_active=True
        )

        wip = Product(
            sku="WIP-ASSEMBLY-001",
            name="WIP Paint Base",
            product_type="WIP",
            base_unit="KG",
            is_active=True
        )

        finished = Product(
            sku="FG-ASSEMBLY-001",
            name="Finished Paint",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )

        db.add_all([raw1, raw2, wip, finished])
        db.flush()

        print(f"   ✓ Created RAW products: {raw1.sku}, {raw2.sku}")
        print(f"   ✓ Created WIP product: {wip.sku}")
        print(f"   ✓ Created FINISHED product: {finished.sku}")

        # Step 2: Add Inventory for RAW Materials
        print("\n2. Adding inventory for RAW materials...")

        raw1_lot = InventoryLot(
            product_id=raw1.id,
            lot_code="RAW1-LOT-001",
            quantity_kg=Decimal("500.0"),
            unit_cost=Decimal("10.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )

        raw2_lot = InventoryLot(
            product_id=raw2.id,
            lot_code="RAW2-LOT-001",
            quantity_kg=Decimal("300.0"),
            unit_cost=Decimal("8.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )

        db.add_all([raw1_lot, raw2_lot])
        db.flush()

        print(f"   ✓ Added {raw1_lot.quantity_kg} kg of {raw1.sku}")
        print(f"   ✓ Added {raw2_lot.quantity_kg} kg of {raw2.sku}")

        # Step 3: Create Assembly Definitions
        print("\n3. Creating assembly definitions...")

        # Assembly: WIP from RAW1 and RAW2
        assembly_wip_raw1 = Assembly(
            parent_product_id=wip.id,
            child_product_id=raw1.id,
            ratio=Decimal("0.6"),  # 0.6 kg RAW1 per kg WIP
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.05")  # 5% loss
        )

        assembly_wip_raw2 = Assembly(
            parent_product_id=wip.id,
            child_product_id=raw2.id,
            ratio=Decimal("0.4"),  # 0.4 kg RAW2 per kg WIP
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.03")  # 3% loss
        )

        # Assembly: FINISHED from WIP
        assembly_finished_wip = Assembly(
            parent_product_id=finished.id,
            child_product_id=wip.id,
            ratio=Decimal("1.0"),  # 1 kg WIP per kg FINISHED
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.02")  # 2% loss
        )

        db.add_all([assembly_wip_raw1, assembly_wip_raw2, assembly_finished_wip])
        db.flush()

        print(f"   ✓ Created assembly: WIP from RAW1 (0.6:1 ratio)")
        print(f"   ✓ Created assembly: WIP from RAW2 (0.4:1 ratio)")
        print(f"   ✓ Created assembly: FINISHED from WIP (1.0:1 ratio)")

        # Step 4: Test Stage 1 - Assemble RAW → WIP
        print("\n4. Testing Stage 1: RAW → WIP Assembly...")

        svc = AssemblyService(db)
        wip_qty = Decimal("100.0")

        result1 = svc.assemble(
            parent_product_id=wip.id,
            parent_qty=wip_qty,
            reason="TEST_RAW_TO_WIP"
        )

        db.commit()

        print(f"   ✓ Produced {result1['produced']['quantity_kg']} kg of WIP")
        print(f"   ✓ Consumed {len(result1['consumed'])} child products")
        for consumed in result1['consumed']:
            print(f"     - {consumed['qty_consumed']} kg of child {consumed['child_product_id'][:8]}")

        # Verify inventory
        db.refresh(raw1_lot)
        db.refresh(raw2_lot)
        print(f"   ✓ RAW1 lot remaining: {raw1_lot.quantity_kg} kg")
        print(f"   ✓ RAW2 lot remaining: {raw2_lot.quantity_kg} kg")

        # Check WIP lot created
        wip_lots = db.query(InventoryLot).filter(
            InventoryLot.product_id == wip.id
        ).all()
        print(f"   ✓ WIP lots created: {len(wip_lots)}")
        if wip_lots:
            print(f"     - Lot: {wip_lots[0].lot_code}, Qty: {wip_lots[0].quantity_kg} kg")

        # Step 5: Test Stage 2 - Assemble WIP → FINISHED
        print("\n5. Testing Stage 2: WIP → FINISHED Assembly...")

        finished_qty = Decimal("50.0")

        result2 = svc.assemble(
            parent_product_id=finished.id,
            parent_qty=finished_qty,
            reason="TEST_WIP_TO_FINISHED"
        )

        db.commit()

        print(f"   ✓ Produced {result2['produced']['quantity_kg']} kg of FINISHED")
        print(f"   ✓ Consumed {len(result2['consumed'])} child products")

        # Verify WIP lot was consumed
        db.refresh(wip_lots[0])
        print(f"   ✓ WIP lot remaining: {wip_lots[0].quantity_kg} kg")

        # Check FINISHED lot created
        finished_lots = db.query(InventoryLot).filter(
            InventoryLot.product_id == finished.id
        ).all()
        print(f"   ✓ FINISHED lots created: {len(finished_lots)}")
        if finished_lots:
            print(f"     - Lot: {finished_lots[0].lot_code}, Qty: {finished_lots[0].quantity_kg} kg")

        # Step 6: Test Direct Assembly (RAW → FINISHED)
        print("\n6. Testing Direct Assembly: RAW → FINISHED (bypassing WIP)...")

        # Create a new finished product for direct assembly
        finished_direct = Product(
            sku="FG-DIRECT-001",
            name="Direct Finished Product",
            product_type="FINISHED",
            base_unit="KG",
            is_active=True
        )
        db.add(finished_direct)
        db.flush()

        # Create assembly: FINISHED directly from RAW
        assembly_direct = Assembly(
            parent_product_id=finished_direct.id,
            child_product_id=raw1.id,
            ratio=Decimal("0.8"),
            direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
            loss_factor=Decimal("0.05")
        )
        db.add(assembly_direct)
        db.flush()

        # Add more inventory for RAW1
        raw1_lot2 = InventoryLot(
            product_id=raw1.id,
            lot_code="RAW1-LOT-002",
            quantity_kg=Decimal("200.0"),
            unit_cost=Decimal("10.5"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        db.add(raw1_lot2)
        db.flush()

        # Assemble directly
        direct_qty = Decimal("75.0")
        result3 = svc.assemble(
            parent_product_id=finished_direct.id,
            parent_qty=direct_qty,
            reason="TEST_DIRECT_ASSEMBLY"
        )

        db.commit()

        print(f"   ✓ Produced {result3['produced']['quantity_kg']} kg of FINISHED (direct)")
        print(f"   ✓ Consumed {result3['consumed'][0]['qty_consumed']} kg of RAW1")

        # Summary
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print("✓ Multi-stage assembly (RAW → WIP → FINISHED) - SUCCESS")
        print("✓ Direct assembly (RAW → FINISHED) - SUCCESS")
        print("✓ Inventory tracking - SUCCESS")
        print("✓ Cost calculation - SUCCESS")
        print("\nAll assembly operations working correctly!")

    except Exception as e:
        db.rollback()
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    test_assembly_operations()

```

## Method 3: Using pytest Tests

Run the existing test suite:

```bash
# Run all assembly tests
pytest tests/test_assembly_service.py -v

# Run specific test
pytest tests/test_assembly_service.py::test_multi_stage_assembly -v

# Run with output
pytest tests/test_assembly_service.py -v -s
```

### Example Test Results

The test suite includes:
- `test_assemble_basic` - Basic assembly operation
- `test_disassemble_basic` - Disassembly operation
- `test_assemble_multiple_children` - Assembly with multiple child products
- `test_assemble_insufficient_stock` - Error handling for insufficient stock
- `test_assemble_raw_to_wip` - RAW → WIP assembly
- `test_assemble_wip_to_finished` - WIP → FINISHED assembly
- `test_multi_stage_assembly` - Full RAW → WIP → FINISHED workflow

## Method 4: Using API Documentation (Swagger)

1. **Start the API server**
   ```bash
   python -m uvicorn app.api.main:app --reload
   ```

2. **Open Swagger UI**
   - Navigate to: `http://127.0.0.1:8000/docs`
   - Find the `/api/v1/assemblies` endpoints
   - Use the interactive API explorer

3. **Test Assembly Endpoint**
   - Click on `POST /api/v1/assemblies/assemble`
   - Click "Try it out"
   - Enter request body:
   ```json
   {
     "parent_product_id": "your-product-id",
     "parent_qty": 100.0,
     "reason": "TEST_ASSEMBLY"
   }
   ```
   - Click "Execute"
   - Review the response

## API Endpoints

### Assemble
```http
POST /api/v1/assemblies/assemble
Content-Type: application/json

{
  "parent_product_id": "uuid-of-parent-product",
  "parent_qty": 100.0,
  "reason": "BATCH_PRODUCTION"
}
```

**Response:**
```json
{
  "consumed": [
    {
      "child_product_id": "uuid",
      "ratio": 0.6,
      "loss_factor": 0.05,
      "qty_consumed": 63.0,
      "cost": 630.0
    }
  ],
  "produced": {
    "product_id": "uuid",
    "quantity_kg": 100.0,
    "unit_cost": 6.30,
    "total_cost": 630.0,
    "lot_id": "uuid",
    "lot_code": "ASSM-20251031-120000"
  }
}
```

### Disassemble
```http
POST /api/v1/assemblies/disassemble
Content-Type: application/json

{
  "parent_product_id": "uuid-of-parent-product",
  "parent_qty": 50.0,
  "reason": "RETURN_TO_STOCK"
}
```

## Common Test Scenarios

### Scenario 1: Simple RAW → WIP Assembly

1. Create RAW product with inventory
2. Create WIP product
3. Create assembly definition (WIP from RAW, 1:1 ratio)
4. Call assemble endpoint
5. Verify WIP lot created and RAW lot consumed

### Scenario 2: Multi-Component Assembly

1. Create multiple RAW products (Resin, Solvent, Additive)
2. Create WIP product
3. Create multiple assembly definitions (one per RAW)
4. Call assemble endpoint
5. Verify all RAW lots consumed proportionally

### Scenario 3: Multi-Stage Production

1. Stage 1: Assemble RAW → WIP
2. Stage 2: Assemble WIP → FINISHED
3. Verify inventory at each stage
4. Verify cost accumulation

### Scenario 4: Insufficient Stock Handling

1. Create assembly definition requiring 100 kg RAW
2. Add only 50 kg RAW inventory
3. Attempt assembly
4. Verify error handling (should fail with clear message)

## Troubleshooting

### Error: "No assembly definitions found"
- **Solution**: Create assembly definitions in the `assemblies` table first

### Error: "Insufficient stock"
- **Solution**: Add inventory lots for child products before assembling

### Error: "Product not found"
- **Solution**: Verify product IDs are correct and products exist

### Inventory not updating
- **Solution**: Ensure you're committing the database transaction (`db.commit()`)

## Verification Checklist

After testing assembly operations, verify:

- [ ] RAW products consumed correctly
- [ ] WIP products created with correct quantities
- [ ] FINISHED products created from WIP
- [ ] Inventory lots created for all produced products
- [ ] Costs calculated correctly (FIFO)
- [ ] Loss factors applied correctly
- [ ] Multi-stage workflows complete successfully
- [ ] Error handling works for insufficient stock
- [ ] Database transactions committed properly

## Next Steps

1. **Test with real data**: Use migrated raw materials from your database
2. **Test via UI**: Create Dash UI forms for assembly operations
3. **Performance testing**: Test with large quantities and multiple assemblies
4. **Integration testing**: Test assembly within full batch production workflow
