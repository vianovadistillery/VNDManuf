from decimal import Decimal
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.assembly_service import AssemblyService
from app.adapters.db.models import Product, InventoryLot
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection


def test_assemble_basic(db_session: Session):
    """
    Test basic assembly operation.
    """
    # Create parent and child products
    parent = Product(
        sku="PARENT-001",
        name="Parent Product",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(parent)
    db_session.flush()
    
    child = Product(
        sku="CHILD-001",
        name="Child Product",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(child)
    db_session.flush()
    
    # Create assembly definition
    assembly = Assembly(
        parent_product_id=parent.id,
        child_product_id=child.id,
        ratio=Decimal("2.0"),  # 2 units of child per unit of parent
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.05")  # 5% loss
    )
    db_session.add(assembly)
    db_session.flush()
    
    # Create child inventory
    child_lot = InventoryLot(
        product_id=child.id,
        lot_code="CHILD-LOT-001",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    db_session.add(child_lot)
    db_session.flush()
    
    # Assemble parent
    svc = AssemblyService(db_session)
    result = svc.assemble(parent.id, Decimal("10.0"), "TEST_ASSEMBLE")
    db_session.commit()
    
    # Verify results
    assert result["produced"]["quantity_kg"] == Decimal("10.0")
    assert result["produced"]["product_id"] == parent.id
    assert len(result["consumed"]) == 1
    assert result["consumed"][0]["qty_consumed"] == Decimal("21.0")  # 10 * 2 * 1.05
    
    # Check child lot was consumed
    db_session.refresh(child_lot)
    assert child_lot.quantity_kg == Decimal("79.0")  # 100 - 21


def test_disassemble_basic(db_session: Session):
    """
    Test basic disassembly operation.
    """
    # Create parent and child products
    parent = Product(
        sku="PARENT-002",
        name="Parent Product",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(parent)
    db_session.flush()
    
    child = Product(
        sku="CHILD-002",
        name="Child Product",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(child)
    db_session.flush()
    
    # Create assembly definition
    assembly = Assembly(
        parent_product_id=parent.id,
        child_product_id=child.id,
        ratio=Decimal("2.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.05")
    )
    db_session.add(assembly)
    db_session.flush()
    
    # Create parent inventory
    parent_lot = InventoryLot(
        product_id=parent.id,
        lot_code="PARENT-LOT-001",
        quantity_kg=Decimal("50.0"),
        unit_cost=Decimal("25.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    db_session.add(parent_lot)
    db_session.flush()
    
    # Disassemble parent
    svc = AssemblyService(db_session)
    result = svc.disassemble(parent.id, Decimal("10.0"), "TEST_DISASSEMBLE")
    db_session.commit()
    
    # Verify results
    assert result["consumed"]["quantity_kg"] == Decimal("10.0")
    assert len(result["produced"]) == 1
    # Child produced = 10 * 2 * 0.95 = 19.0 (accounting for loss)
    assert result["produced"][0]["qty_produced"] == Decimal("19.0")
    
    # Check parent lot was consumed
    db_session.refresh(parent_lot)
    assert parent_lot.quantity_kg == Decimal("40.0")


def test_assemble_multiple_children(db_session: Session):
    """
    Test assembly with multiple child products.
    """
    # Create products
    parent = Product(sku="PARENT-003", name="Parent", base_unit="KG")
    child1 = Product(sku="CHILD-003A", name="Child A", base_unit="KG")
    child2 = Product(sku="CHILD-003B", name="Child B", base_unit="KG")
    
    for p in [parent, child1, child2]:
        db_session.add(p)
    db_session.flush()
    
    # Create assembly definitions
    assembly1 = Assembly(
        parent_product_id=parent.id,
        child_product_id=child1.id,
        ratio=Decimal("1.5"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    assembly2 = Assembly(
        parent_product_id=parent.id,
        child_product_id=child2.id,
        ratio=Decimal("0.5"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    db_session.add_all([assembly1, assembly2])
    db_session.flush()
    
    # Create child inventory
    child1_lot = InventoryLot(
        product_id=child1.id, lot_code="C1-001",
        quantity_kg=Decimal("100.0"), unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(), is_active=True
    )
    child2_lot = InventoryLot(
        product_id=child2.id, lot_code="C2-001",
        quantity_kg=Decimal("100.0"), unit_cost=Decimal("20.0"),
        received_at=datetime.utcnow(), is_active=True
    )
    db_session.add_all([child1_lot, child2_lot])
    db_session.flush()
    
    # Assemble parent
    svc = AssemblyService(db_session)
    result = svc.assemble(parent.id, Decimal("10.0"), "TEST_MULTI")
    db_session.commit()
    
    # Verify both children were consumed
    assert len(result["consumed"]) == 2
    
    # Check quantities
    child1_consumed = next(c for c in result["consumed"] if c["child_product_id"] == child1.id)
    child2_consumed = next(c for c in result["consumed"] if c["child_product_id"] == child2.id)
    
    assert child1_consumed["qty_consumed"] == Decimal("15.0")  # 10 * 1.5
    assert child2_consumed["qty_consumed"] == Decimal("5.0")   # 10 * 0.5


def test_assemble_insufficient_stock(db_session: Session):
    """
    Test assembly fails when insufficient child inventory.
    """
    # Create products
    parent = Product(sku="PARENT-004", name="Parent", base_unit="KG")
    child = Product(sku="CHILD-004", name="Child", base_unit="KG")
    
    for p in [parent, child]:
        db_session.add(p)
    db_session.flush()
    
    # Create assembly
    assembly = Assembly(
        parent_product_id=parent.id,
        child_product_id=child.id,
        ratio=Decimal("2.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    db_session.add(assembly)
    db_session.flush()
    
    # Create limited child inventory
    child_lot = InventoryLot(
        product_id=child.id,
        lot_code="CHILD-LOT-002",
        quantity_kg=Decimal("10.0"),  # Not enough for 10 units of parent (need 20)
        unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    db_session.add(child_lot)
    db_session.flush()
    
    # Try to assemble - should fail
    svc = AssemblyService(db_session)
    try:
        svc.assemble(parent.id, Decimal("10.0"), "TEST_FAIL")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Insufficient stock" in str(e)

