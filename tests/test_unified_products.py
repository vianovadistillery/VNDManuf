"""Tests for unified products structure (RAW/WIP/FINISHED)."""

from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

from app.adapters.db.models import Product, Formula, FormulaLine, InventoryLot


def test_product_types(db_session: Session):
    """Test creating products with different product types."""
    raw = Product(
        sku="RM-001",
        name="Raw Material",
        product_type="RAW",
        base_unit="KG",
        raw_material_code=1001,
        specific_gravity=Decimal("1.2"),
        usage_cost=Decimal("5.50")
    )
    
    wip = Product(
        sku="WIP-001",
        name="Work In Progress",
        product_type="WIP",
        base_unit="KG"
    )
    
    finished = Product(
        sku="FG-001",
        name="Finished Good",
        product_type="FINISHED",
        base_unit="KG",
        formula_id=None
    )
    
    db_session.add_all([raw, wip, finished])
    db_session.commit()
    
    # Verify products were created with correct types
    assert raw.product_type == "RAW"
    assert raw.raw_material_code == 1001
    assert raw.specific_gravity == Decimal("1.2")
    
    assert wip.product_type == "WIP"
    
    assert finished.product_type == "FINISHED"


def test_formula_line_with_unified_products(db_session: Session):
    """Test formula lines using unified products."""
    # Create raw material product
    raw1 = Product(
        sku="RM-101",
        name="Resin A",
        product_type="RAW",
        base_unit="KG",
        usage_cost=Decimal("10.0")
    )
    raw2 = Product(
        sku="RM-102",
        name="Solvent B",
        product_type="RAW",
        base_unit="KG",
        usage_cost=Decimal("8.0")
    )
    
    finished = Product(
        sku="FG-101",
        name="Finished Product",
        product_type="FINISHED",
        base_unit="KG"
    )
    
    db_session.add_all([raw1, raw2, finished])
    db_session.flush()
    
    # Create formula
    formula = Formula(
        product_id=finished.id,
        formula_code="FORMULA-101",
        formula_name="Test Formula",
        version=1
    )
    db_session.add(formula)
    db_session.flush()
    
    # Create formula lines using product_id
    line1 = FormulaLine(
        formula_id=formula.id,
        product_id=raw1.id,  # Using unified product_id
        quantity_kg=Decimal("50.0"),
        sequence=1,
        unit="KG"
    )
    
    line2 = FormulaLine(
        formula_id=formula.id,
        product_id=raw2.id,  # Using unified product_id
        quantity_kg=Decimal("30.0"),
        sequence=2,
        unit="KG"
    )
    
    db_session.add_all([line1, line2])
    db_session.commit()
    
    # Verify formula lines
    assert line1.product_id == raw1.id
    assert line1.product.sku == "RM-101"
    assert line2.product_id == raw2.id
    assert line2.product.sku == "RM-102"
    
    # Test backward compatibility property
    assert line1.raw_material.sku == "RM-101"  # Should work via property
    assert line1.raw_material == line1.product


def test_inventory_lot_unified_products(db_session: Session):
    """Test inventory lots work with all product types."""
    raw = Product(sku="RM-201", name="Raw", product_type="RAW", base_unit="KG")
    wip = Product(sku="WIP-201", name="WIP", product_type="WIP", base_unit="KG")
    finished = Product(sku="FG-201", name="Finished", product_type="FINISHED", base_unit="KG")
    
    db_session.add_all([raw, wip, finished])
    db_session.flush()
    
    # Create inventory lots for each type
    raw_lot = InventoryLot(
        product_id=raw.id,
        lot_code="RAW-LOT-001",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("5.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    
    wip_lot = InventoryLot(
        product_id=wip.id,
        lot_code="WIP-LOT-001",
        quantity_kg=Decimal("50.0"),
        unit_cost=Decimal("15.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    
    finished_lot = InventoryLot(
        product_id=finished.id,
        lot_code="FG-LOT-001",
        quantity_kg=Decimal("25.0"),
        unit_cost=Decimal("25.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    
    db_session.add_all([raw_lot, wip_lot, finished_lot])
    db_session.commit()
    
    # Verify lots are linked to products
    assert raw_lot.product.product_type == "RAW"
    assert wip_lot.product.product_type == "WIP"
    assert finished_lot.product.product_type == "FINISHED"


def test_product_type_filtering(db_session: Session):
    """Test filtering products by product_type."""
    # Create products of different types
    products = [
        Product(sku=f"RM-{i}", name=f"Raw {i}", product_type="RAW", base_unit="KG")
        for i in range(3)
    ] + [
        Product(sku=f"WIP-{i}", name=f"WIP {i}", product_type="WIP", base_unit="KG")
        for i in range(2)
    ] + [
        Product(sku=f"FG-{i}", name=f"Finished {i}", product_type="FINISHED", base_unit="KG")
        for i in range(4)
    ]
    
    db_session.add_all(products)
    db_session.commit()
    
    # Test filtering
    raw_count = db_session.query(Product).filter(Product.product_type == "RAW").count()
    wip_count = db_session.query(Product).filter(Product.product_type == "WIP").count()
    finished_count = db_session.query(Product).filter(Product.product_type == "FINISHED").count()
    
    assert raw_count == 3
    assert wip_count == 2
    assert finished_count == 4

