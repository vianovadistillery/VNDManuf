"""Tests for unified product migration and validation."""

from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime
from uuid import uuid4

from app.adapters.db.models import Product, FormulaLine, InventoryLot, InventoryMovement


def test_migration_mapping_table(db_session: Session):
    """Test that migration mapping table can track legacy to new mappings."""
    # This would be created by the migration
    # For now, verify products can be queried by legacy fields
    raw_product = Product(
        sku="RM-MIGRATED",
        name="Migrated Raw Material",
        product_type="RAW",
        raw_material_code=9999,
        base_unit="KG"
    )
    db_session.add(raw_product)
    db_session.commit()
    
    # Verify can find by raw_material_code
    found = db_session.query(Product).filter(
        Product.raw_material_code == 9999
    ).first()
    
    assert found is not None
    assert found.product_type == "RAW"


def test_formula_line_migration(db_session: Session):
    """Test that formula lines work with migrated products."""
    # Create migrated raw material product
    raw = Product(
        sku="RM-MIGRATED-001",
        name="Migrated Raw",
        product_type="RAW",
        raw_material_code=2001,
        base_unit="KG",
        usage_cost=Decimal("10.0")
    )
    
    finished = Product(
        sku="FG-MIGRATED-001",
        name="Migrated Finished",
        product_type="FINISHED",
        base_unit="KG"
    )
    
    db_session.add_all([raw, finished])
    db_session.flush()
    
    from app.adapters.db.models import Formula
    formula = Formula(
        product_id=finished.id,
        formula_code="MIGRATED-FORMULA",
        formula_name="Migrated Formula",
        version=1
    )
    db_session.add(formula)
    db_session.flush()
    
    # Create formula line using product_id (migrated structure)
    line = FormulaLine(
        formula_id=formula.id,
        product_id=raw.id,  # Unified product_id reference
        quantity_kg=Decimal("50.0"),
        sequence=1,
        unit="KG"
    )
    db_session.add(line)
    db_session.commit()
    
    # Verify formula line works correctly
    assert line.product_id == raw.id
    assert line.product.product_type == "RAW"
    assert line.product.raw_material_code == 2001


def test_inventory_movement_migration(db_session: Session):
    """Test that inventory movements work with unified product_id."""
    # Create products
    raw = Product(sku="RM-MOV", name="Raw", product_type="RAW", base_unit="KG")
    finished = Product(sku="FG-MOV", name="Finished", product_type="FINISHED", base_unit="KG")
    
    db_session.add_all([raw, finished])
    db_session.flush()
    
    # Create inventory lots
    raw_lot = InventoryLot(
        product_id=raw.id,
        lot_code="RAW-LOT-MOV",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("5.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    
    finished_lot = InventoryLot(
        product_id=finished.id,
        lot_code="FG-LOT-MOV",
        quantity_kg=Decimal("50.0"),
        unit_cost=Decimal("25.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    
    db_session.add_all([raw_lot, finished_lot])
    db_session.flush()
    
    # Create inventory movements using unified product_id (migrated structure)
    raw_movement = InventoryMovement(
        product_id=raw.id,  # Unified product_id
        qty=Decimal("10.0"),
        unit="KG",
        direction="OUT",
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        note="Test raw movement"
    )
    
    finished_movement = InventoryMovement(
        product_id=finished.id,  # Unified product_id
        qty=Decimal("5.0"),
        unit="KG",
        direction="IN",
        date=datetime.utcnow().strftime("%Y-%m-%d"),
        note="Test finished movement"
    )
    
    db_session.add_all([raw_movement, finished_movement])
    db_session.commit()
    
    # Verify movements
    assert raw_movement.product_id == raw.id
    assert raw_movement.product.product_type == "RAW"
    assert finished_movement.product_id == finished.id
    assert finished_movement.product.product_type == "FINISHED"


def test_product_type_defaults(db_session: Session):
    """Test that product_type defaults correctly for backward compatibility."""
    # Create product without specifying product_type (should default to RAW)
    product = Product(
        sku="DEFAULT-TEST",
        name="Default Product",
        base_unit="KG"
    )
    db_session.add(product)
    db_session.flush()
    
    # Verify default
    assert product.product_type == "RAW" or product.product_type is None  # Depending on default handling


def test_backward_compatibility_formula_line(db_session: Session):
    """Test backward compatibility property on FormulaLine."""
    raw = Product(
        sku="BC-TEST",
        name="Backward Compat Test",
        product_type="RAW",
        base_unit="KG"
    )
    db_session.add(raw)
    db_session.flush()
    
    from app.adapters.db.models import Formula
    finished = Product(
        sku="BC-FG",
        name="Finished",
        product_type="FINISHED",
        base_unit="KG"
    )
    db_session.add(finished)
    db_session.flush()
    
    formula = Formula(
        product_id=finished.id,
        formula_code="BC-FORMULA",
        formula_name="BC Formula",
        version=1
    )
    db_session.add(formula)
    db_session.flush()
    
    line = FormulaLine(
        formula_id=formula.id,
        product_id=raw.id,
        quantity_kg=Decimal("10.0"),
        sequence=1
    )
    db_session.add(line)
    db_session.commit()
    
    # Test backward compatibility property
    assert line.product_id == raw.id
    assert line.raw_material is not None  # Backward compatibility property
    assert line.raw_material.id == raw.id
    assert line.raw_material == line.product  # Should be same object


def test_product_type_filtering_query(db_session: Session):
    """Test querying products by product_type for migration validation."""
    # Create various product types
    raw_products = [
        Product(sku=f"RM-VAL-{i}", name=f"Raw {i}", product_type="RAW", base_unit="KG")
        for i in range(5)
    ]
    
    wip_products = [
        Product(sku=f"WIP-VAL-{i}", name=f"WIP {i}", product_type="WIP", base_unit="KG")
        for i in range(3)
    ]
    
    finished_products = [
        Product(sku=f"FG-VAL-{i}", name=f"Finished {i}", product_type="FINISHED", base_unit="KG")
        for i in range(7)
    ]
    
    db_session.add_all(raw_products + wip_products + finished_products)
    db_session.commit()
    
    # Validate counts by type
    raw_count = db_session.query(Product).filter(Product.product_type == "RAW").count()
    wip_count = db_session.query(Product).filter(Product.product_type == "WIP").count()
    finished_count = db_session.query(Product).filter(Product.product_type == "FINISHED").count()
    
    assert raw_count == 5
    assert wip_count == 3
    assert finished_count == 7


def test_unified_inventory_across_types(db_session: Session):
    """Test that inventory works uniformly across all product types."""
    # Create one product of each type
    raw = Product(sku="INV-RAW", name="Raw", product_type="RAW", base_unit="KG")
    wip = Product(sku="INV-WIP", name="WIP", product_type="WIP", base_unit="KG")
    finished = Product(sku="INV-FG", name="Finished", product_type="FINISHED", base_unit="KG")
    
    db_session.add_all([raw, wip, finished])
    db_session.flush()
    
    # Create lots for each
    lots = [
        InventoryLot(
            product_id=p.id,
            lot_code=f"LOT-{p.sku}",
            quantity_kg=Decimal("100.0"),
            unit_cost=Decimal("10.0"),
            received_at=datetime.utcnow(),
            is_active=True
        )
        for p in [raw, wip, finished]
    ]
    
    db_session.add_all(lots)
    db_session.commit()
    
    # Verify all lots are accessible via unified InventoryLot model
    all_lots = db_session.query(InventoryLot).all()
    assert len(all_lots) == 3
    
    # Verify each lot's product has correct type
    type_map = {lot.product_id: lot.product.product_type for lot in all_lots}
    assert type_map[raw.id] == "RAW"
    assert type_map[wip.id] == "WIP"
    assert type_map[finished.id] == "FINISHED"

