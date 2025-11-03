# Post-Migration Tasks & Verification Checklist

This document outlines the remaining tasks after the unified products migration completion.

## Immediate Verification Tasks

### ✅ Completed
- [x] Migration script executed successfully
- [x] Database schema unified (RAW/WIP/FINISHED in products table)
- [x] Data migrated (11 raw materials → 13 products)
- [x] Formula lines updated to use product_id
- [x] All tests passing (21/21)
- [x] Test script created for assembly operations

### 🔄 Pending Verification

#### 1. Verify API Endpoints with Product Type Filtering
**Status**: Pending
**Priority**: High
**Estimated Time**: 30 minutes

**Tasks**:
- [ ] Test `GET /api/v1/products?product_type=RAW` - verify only RAW products returned
- [ ] Test `GET /api/v1/products?product_type=WIP` - verify only WIP products returned
- [ ] Test `GET /api/v1/products?product_type=FINISHED` - verify only FINISHED products returned
- [ ] Test `GET /api/v1/products` - verify all products returned when no filter
- [ ] Verify product_type field included in all responses
- [ ] Test product creation with different product_type values
- [ ] Test product update with product_type changes

**Test Commands**:
```bash
# PowerShell examples
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=RAW" -Method GET
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=WIP" -Method GET
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/v1/products?product_type=FINISHED" -Method GET
```

#### 2. Test via API Using Swagger UI
**Status**: Pending
**Priority**: High
**Estimated Time**: 1 hour

**Tasks**:
- [ ] Start API server: `python -m uvicorn app.api.main:app --reload`
- [ ] Open Swagger UI: `http://127.0.0.1:8000/docs`
- [ ] Test product endpoints:
  - [ ] Create RAW product
  - [ ] Create WIP product
  - [ ] Create FINISHED product
  - [ ] List products with type filtering
  - [ ] Update product type
- [ ] Test assembly endpoints:
  - [ ] POST /api/v1/assemblies/assemble
  - [ ] POST /api/v1/assemblies/disassemble
  - [ ] Verify request/response formats
- [ ] Test batch endpoints with WIP creation:
  - [ ] Finish batch with `create_wip=true`
  - [ ] Verify WIP product created
  - [ ] Verify inventory lots created

#### 3. Test with Real Data
**Status**: Pending
**Priority**: Medium
**Estimated Time**: 1 hour

**Tasks**:
- [ ] Query migrated raw materials from database:
  ```python
  # Get migrated products
  db.query(Product).filter(Product.product_type == 'RAW').all()
  ```
- [ ] Test assembly operations with migrated products:
  - [ ] Use actual raw material SKUs
  - [ ] Verify assembly definitions work with migrated products
  - [ ] Test inventory consumption with real data
- [ ] Verify formula_lines work with migrated products:
  - [ ] Check existing formulas still work
  - [ ] Verify cost calculations correct
- [ ] Test batch operations with migrated products

**Script**:
```bash
# Use existing test script but with migrated products
python scripts/test_assembly_operations.py
# Modify to use migrated product IDs
```

#### 4. Test Error Cases
**Status**: Pending
**Priority**: Medium
**Estimated Time**: 30 minutes

**Tasks**:
- [ ] Test insufficient stock scenarios:
  - [ ] Attempt assembly with insufficient child inventory
  - [ ] Verify proper error message returned
  - [ ] Verify no partial consumption occurred
- [ ] Test invalid product_type:
  - [ ] Attempt to create product with invalid product_type
  - [ ] Verify validation error
- [ ] Test missing assembly definitions:
  - [ ] Attempt assembly without assembly definition
  - [ ] Verify proper error message
- [ ] Test missing products:
  - [ ] Attempt assembly with non-existent product_id
  - [ ] Verify 404 error

**Test Cases**:
```python
# Insufficient stock test
try:
    svc.assemble(parent_id, Decimal("1000.0"), "TEST")  # More than available
except ValueError as e:
    assert "Insufficient stock" in str(e)
```

#### 5. Integrate with Batch Production
**Status**: Pending
**Priority**: High
**Estimated Time**: 2 hours

**Tasks**:
- [ ] Test batch completion with WIP creation:
  - [ ] Create work order for finished product
  - [ ] Create and release batch
  - [ ] Finish batch with `create_wip=True`
  - [ ] Verify WIP product created
  - [ ] Verify WIP inventory lot created
  - [ ] Verify batch status updated
- [ ] Test multi-stage batch workflow:
  - [ ] Stage 1: Batch creates WIP
  - [ ] Stage 2: Assemble WIP to FINISHED
  - [ ] Verify complete workflow
- [ ] Test batch with existing WIP product:
  - [ ] Use existing WIP product when finishing batch
  - [ ] Verify inventory added to existing WIP lot
- [ ] Verify batch ticket generation works with unified products
- [ ] Test batch component consumption with unified products

**Integration Test**:
```python
# Full workflow test
1. Create RAW products with inventory
2. Create FINISHED product with formula
3. Create work order
4. Create and release batch
5. Finish batch (creates WIP or FINISHED directly)
6. Verify inventory movements
7. Verify cost tracking
```

## Future Cleanup Tasks

### 6. Clean Up Legacy Tables
**Status**: Pending
**Priority**: Low
**Estimated Time**: 1 hour
**Timeline**: After 30-day verification period

**Tasks**:
- [ ] Verify all code using legacy tables migrated
- [ ] Backup database
- [ ] Create migration to drop legacy tables:
  - [ ] `raw_materials` table
  - [ ] `finished_goods` table
- [ ] Test migration on backup
- [ ] Apply to production
- [ ] Update documentation

**Migration Script Template**:
```python
def upgrade():
    # Verify no references to legacy tables
    # Drop tables
    op.drop_table('raw_materials')
    op.drop_table('finished_goods')
```

### 7. Remove Legacy Columns
**Status**: Pending
**Priority**: Low
**Estimated Time**: 1 hour
**Timeline**: After all code migrated and verified

**Tasks**:
- [ ] Verify no code uses legacy columns:
  - [ ] Search codebase for `raw_material_id`
  - [ ] Search codebase for `item_type`
  - [ ] Search codebase for `item_id`
- [ ] Create migration to drop columns:
  - [ ] `formula_lines.raw_material_id`
  - [ ] `inventory_movements.item_type`
  - [ ] `inventory_movements.item_id`
- [ ] Test migration
- [ ] Apply to production

**Note**: Keep backward compatibility property `FormulaLine.raw_material` until columns removed.

## Verification Checklist

Before considering migration complete:

- [ ] All API endpoints tested and working
- [ ] Product type filtering verified
- [ ] Assembly operations tested with real data
- [ ] Error handling verified
- [ ] Batch integration tested
- [ ] No regressions in existing functionality
- [ ] Performance acceptable
- [ ] Documentation updated
- [ ] Team trained on new structure

## Testing Resources

### Test Scripts
- `scripts/test_assembly_operations.py` - Assembly operation testing
- `scripts/check_post_migration_state.py` - Post-migration state verification
- `scripts/validate_migration.py` - Migration validation

### Test Suites
- `pytest tests/test_unified_products.py` - Unified product tests
- `pytest tests/test_wip_batching.py` - WIP batch creation tests
- `pytest tests/test_assembly_service.py` - Assembly service tests
- `pytest tests/test_unified_migration.py` - Migration tests

### Documentation
- `docs/TESTING_ASSEMBLY_OPERATIONS.md` - Assembly testing guide
- `docs/UNIFIED_PRODUCTS_MIGRATION.md` - Migration guide
- `MIGRATION_COMPLETE.md` - Migration completion summary

## Progress Tracking

Update this document as tasks are completed:

**Last Updated**: 2025-10-31
**Completed**: 1/7 tasks
**In Progress**: 0/7 tasks
**Pending**: 6/7 tasks

---

## Notes

- Legacy tables (`raw_materials`, `finished_goods`) are preserved for reference
- Backward compatibility maintained via `FormulaLine.raw_material` property
- All migrations are idempotent and can be re-run safely
- Backup created: `tpmanuf.db.backup_before_unified_migration`
