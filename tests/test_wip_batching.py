"""Tests for WIP product creation in batch completion."""

from decimal import Decimal
from uuid import uuid4

from sqlalchemy.orm import Session

from app.adapters.db.models import (
    Batch,
    Formula,
    InventoryLot,
    InventoryTxn,
    Product,
    WorkOrder,
)
from app.services.batching import BatchingService


def test_finish_batch_create_wip(db_session: Session):
    """Test creating WIP product when finishing a batch."""
    # Create product and formula
    product = Product(
        sku="TEST-PRODUCT", name="Test Product", product_type="FINISHED", base_unit="KG"
    )
    db_session.add(product)
    db_session.flush()

    formula = Formula(
        id=str(uuid4()),
        product_id=product.id,
        formula_code="TEST-FORMULA",
        formula_name="Test Formula",
        version=1,
    )
    db_session.add(formula)
    db_session.flush()

    # Create work order
    work_order = WorkOrder(
        id=str(uuid4()),
        code="WO-001",
        product_id=product.id,
        formula_id=formula.id,
        quantity_kg=Decimal("100.0"),
        status="RELEASED",
    )
    db_session.add(work_order)
    db_session.flush()

    # Create batch
    batch = Batch(
        id=str(uuid4()),
        work_order_id=work_order.id,
        batch_code="BATCH-001",
        quantity_kg=Decimal("100.0"),
        status="RELEASED",
        batch_status="in_process",
    )
    db_session.add(batch)
    db_session.flush()

    # Finish batch with WIP creation
    service = BatchingService(db_session)
    finished_batch = service.finish_batch(
        batch.id, qty_fg_kg=Decimal("95.0"), create_wip=True, notes="Test WIP creation"
    )
    db_session.commit()

    # Verify batch was completed
    assert finished_batch.status == "COMPLETED"
    assert finished_batch.yield_actual == Decimal("95.0")

    # Verify WIP product was created
    wip_products = (
        db_session.query(Product)
        .filter(Product.product_type == "WIP", Product.sku.like(f"WIP-{product.sku}%"))
        .all()
    )

    assert len(wip_products) == 1
    wip_product = wip_products[0]
    assert wip_product.product_type == "WIP"
    assert "WIP" in wip_product.sku
    assert wip_product.formula_id == formula.id

    # Verify WIP lot was created
    wip_lots = (
        db_session.query(InventoryLot)
        .filter(InventoryLot.product_id == wip_product.id)
        .all()
    )

    assert len(wip_lots) == 1
    wip_lot = wip_lots[0]
    assert wip_lot.quantity_kg == Decimal("95.0")
    assert "WIP" in wip_lot.lot_code

    # Verify receipt transaction
    txn = (
        db_session.query(InventoryTxn)
        .filter(
            InventoryTxn.lot_id == wip_lot.id,
            InventoryTxn.transaction_type == "RECEIPT",
        )
        .first()
    )

    assert txn is not None
    assert txn.quantity_kg == Decimal("95.0")


def test_finish_batch_use_existing_wip(db_session: Session):
    """Test finishing batch using existing WIP product."""
    # Create products
    finished_product = Product(
        sku="FINISHED-001",
        name="Finished Product",
        product_type="FINISHED",
        base_unit="KG",
    )
    wip_product = Product(
        sku="WIP-EXISTING", name="Existing WIP", product_type="WIP", base_unit="KG"
    )
    db_session.add_all([finished_product, wip_product])
    db_session.flush()

    # Create formula
    formula = Formula(
        id=str(uuid4()),
        product_id=finished_product.id,
        formula_code="FORMULA-001",
        formula_name="Test Formula",
        version=1,
    )
    db_session.add(formula)
    db_session.flush()

    # Create work order and batch
    work_order = WorkOrder(
        id=str(uuid4()),
        code="WO-002",
        product_id=finished_product.id,
        formula_id=formula.id,
        quantity_kg=Decimal("50.0"),
        status="RELEASED",
    )
    batch = Batch(
        id=str(uuid4()),
        work_order_id=work_order.id,
        batch_code="BATCH-002",
        quantity_kg=Decimal("50.0"),
        status="RELEASED",
        batch_status="in_process",
    )
    db_session.add_all([work_order, batch])
    db_session.flush()

    # Finish batch using existing WIP product
    service = BatchingService(db_session)
    finished_batch = service.finish_batch(
        batch.id,
        qty_fg_kg=Decimal("48.0"),
        create_wip=True,
        wip_product_id=wip_product.id,
    )
    db_session.commit()

    # Verify WIP lot was created for existing WIP product
    wip_lots = (
        db_session.query(InventoryLot)
        .filter(InventoryLot.product_id == wip_product.id)
        .all()
    )

    assert len(wip_lots) == 1
    assert wip_lots[0].quantity_kg == Decimal("48.0")


def test_finish_batch_to_finished(db_session: Session):
    """Test finishing batch to FINISHED product (default behavior)."""
    # Create finished product
    product = Product(
        sku="FG-001", name="Finished Good", product_type="FINISHED", base_unit="KG"
    )
    db_session.add(product)
    db_session.flush()

    # Create formula and work order
    formula = Formula(
        id=str(uuid4()),
        product_id=product.id,
        formula_code="FORMULA-002",
        formula_name="Test Formula",
        version=1,
    )
    work_order = WorkOrder(
        id=str(uuid4()),
        code="WO-003",
        product_id=product.id,
        formula_id=formula.id,
        quantity_kg=Decimal("75.0"),
        status="RELEASED",
    )
    batch = Batch(
        id=str(uuid4()),
        work_order_id=work_order.id,
        batch_code="BATCH-003",
        quantity_kg=Decimal("75.0"),
        status="RELEASED",
        batch_status="in_process",
    )
    db_session.add_all([formula, work_order, batch])
    db_session.flush()

    # Finish batch (default: FINISHED, not WIP)
    service = BatchingService(db_session)
    finished_batch = service.finish_batch(batch.id, qty_fg_kg=Decimal("73.0"))
    db_session.commit()

    # Verify finished goods lot was created
    fg_lots = (
        db_session.query(InventoryLot)
        .filter(InventoryLot.product_id == product.id)
        .all()
    )

    assert len(fg_lots) == 1
    assert fg_lots[0].quantity_kg == Decimal("73.0")
    assert "FG" in fg_lots[0].lot_code or "BATCH-003" in fg_lots[0].lot_code
