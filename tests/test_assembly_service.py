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
        product_type="FINISHED",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(parent)
    db_session.flush()
    
    child = Product(
        sku="CHILD-001",
        name="Child Product",
        product_type="RAW",
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
        product_type="FINISHED",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add(parent)
    db_session.flush()
    
    child = Product(
        sku="CHILD-002",
        name="Child Product",
        product_type="RAW",
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
    parent = Product(sku="PARENT-003", name="Parent", product_type="FINISHED", base_unit="KG")
    child1 = Product(sku="CHILD-003A", name="Child A", product_type="RAW", base_unit="KG")
    child2 = Product(sku="CHILD-003B", name="Child B", product_type="RAW", base_unit="KG")
    
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
    parent = Product(sku="PARENT-004", name="Parent", product_type="FINISHED", base_unit="KG")
    child = Product(sku="CHILD-004", name="Child", product_type="RAW", base_unit="KG")
    
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


def test_assemble_raw_to_wip(db_session: Session):
    """
    Test assembly from RAW to WIP.
    """
    # Create RAW and WIP products
    raw = Product(
        sku="RAW-001",
        name="Raw Material",
        product_type="RAW",
        base_unit="KG",
        density_kg_per_l=None
    )
    wip = Product(
        sku="WIP-001",
        name="Work In Progress",
        product_type="WIP",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add_all([raw, wip])
    db_session.flush()
    
    # Create assembly: WIP from RAW
    assembly = Assembly(
        parent_product_id=wip.id,
        child_product_id=raw.id,
        ratio=Decimal("1.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    db_session.add(assembly)
    db_session.flush()
    
    # Create raw material inventory
    raw_lot = InventoryLot(
        product_id=raw.id,
        lot_code="RAW-LOT-001",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("5.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    db_session.add(raw_lot)
    db_session.flush()
    
    # Assemble WIP from RAW
    svc = AssemblyService(db_session)
    result = svc.assemble(wip.id, Decimal("50.0"), "RAW_TO_WIP")
    db_session.commit()
    
    # Verify WIP was created
    assert result["produced"]["quantity_kg"] == Decimal("50.0")
    assert result["produced"]["product_id"] == wip.id
    assert len(result["consumed"]) == 1
    assert result["consumed"][0]["qty_consumed"] == Decimal("50.0")
    
    # Check raw lot was consumed
    db_session.refresh(raw_lot)
    assert raw_lot.quantity_kg == Decimal("50.0")  # 100 - 50


def test_assemble_wip_to_finished(db_session: Session):
    """
    Test assembly from WIP to FINISHED.
    """
    # Create WIP and FINISHED products
    wip = Product(
        sku="WIP-002",
        name="Work In Progress",
        product_type="WIP",
        base_unit="KG",
        density_kg_per_l=None
    )
    finished = Product(
        sku="FINISHED-001",
        name="Finished Product",
        product_type="FINISHED",
        base_unit="KG",
        density_kg_per_l=None
    )
    db_session.add_all([wip, finished])
    db_session.flush()
    
    # Create assembly: FINISHED from WIP
    assembly = Assembly(
        parent_product_id=finished.id,
        child_product_id=wip.id,
        ratio=Decimal("1.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.02")  # 2% loss
    )
    db_session.add(assembly)
    db_session.flush()
    
    # Create WIP inventory
    wip_lot = InventoryLot(
        product_id=wip.id,
        lot_code="WIP-LOT-001",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("15.0"),
        received_at=datetime.utcnow(),
        is_active=True
    )
    db_session.add(wip_lot)
    db_session.flush()
    
    # Assemble FINISHED from WIP
    svc = AssemblyService(db_session)
    result = svc.assemble(finished.id, Decimal("50.0"), "WIP_TO_FINISHED")
    db_session.commit()
    
    # Verify FINISHED was created
    assert result["produced"]["quantity_kg"] == Decimal("50.0")
    assert result["produced"]["product_id"] == finished.id
    
    # Check WIP lot was consumed (with loss factor)
    # Need: 50 * 1.0 * 1.02 = 51.0
    db_session.refresh(wip_lot)
    assert wip_lot.quantity_kg == Decimal("49.0")  # 100 - 51


def test_multi_stage_assembly(db_session: Session):
    """
    Test multi-stage assembly: RAW -> WIP -> FINISHED.
    """
    # Create products
    raw = Product(sku="RAW-MULTI", name="Raw", product_type="RAW", base_unit="KG")
    wip = Product(sku="WIP-MULTI", name="WIP", product_type="WIP", base_unit="KG")
    finished = Product(sku="FIN-MULTI", name="Finished", product_type="FINISHED", base_unit="KG")
    db_session.add_all([raw, wip, finished])
    db_session.flush()
    
    # Create assemblies
    raw_to_wip = Assembly(
        parent_product_id=wip.id,
        child_product_id=raw.id,
        ratio=Decimal("1.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    wip_to_finished = Assembly(
        parent_product_id=finished.id,
        child_product_id=wip.id,
        ratio=Decimal("1.0"),
        direction=AssemblyDirection.MAKE_FROM_CHILDREN.value,
        loss_factor=Decimal("0.0")
    )
    db_session.add_all([raw_to_wip, wip_to_finished])
    db_session.flush()
    
    # Create raw inventory
    raw_lot = InventoryLot(
        product_id=raw.id, lot_code="RAW-001",
        quantity_kg=Decimal("100.0"), unit_cost=Decimal("5.0"),
        received_at=datetime.utcnow(), is_active=True
    )
    db_session.add(raw_lot)
    db_session.flush()
    
    # Stage 1: RAW -> WIP
    svc = AssemblyService(db_session)
    result1 = svc.assemble(wip.id, Decimal("50.0"), "STAGE1")
    db_session.commit()
    
    # Stage 2: WIP -> FINISHED
    result2 = svc.assemble(finished.id, Decimal("50.0"), "STAGE2")
    db_session.commit()
    
    # Verify results
    assert result1["produced"]["quantity_kg"] == Decimal("50.0")
    assert result2["produced"]["quantity_kg"] == Decimal("50.0")
    
    # Check raw was fully consumed
    db_session.refresh(raw_lot)
    assert raw_lot.quantity_kg == Decimal("50.0")  # 100 - 50 (from stage 1)

