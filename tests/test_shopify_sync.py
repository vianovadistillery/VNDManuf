from datetime import datetime
from decimal import Decimal
from unittest.mock import patch

from sqlalchemy.orm import Session

from app.adapters.db.models import InventoryLot, Product
from app.adapters.db.models_assemblies_shopify import (
    InventoryReservation,
    ProductChannelLink,
)
from app.services.shopify_sync import ShopifySyncService


def test_available_to_sell_basic(db_session: Session):
    """
    Test calculation of available to sell quantity.
    """
    from app.services.inventory import InventoryService

    # Create product
    product = Product(sku="TEST-001", name="Test Product", base_unit="KG")
    db_session.add(product)
    db_session.flush()

    # Create inventory lot
    lot = InventoryLot(
        product_id=product.id,
        lot_code="LOT-001",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(),
        is_active=True,
    )
    db_session.add(lot)
    db_session.flush()

    # Create reservation
    reservation = InventoryReservation(
        product_id=product.id,
        qty_canonical=Decimal("20.0"),
        source="shopify",
        reference_id="ORDER-001",
        status="ACTIVE",
    )
    db_session.add(reservation)
    db_session.commit()

    # Check available to sell
    inventory = InventoryService(db_session)
    available = inventory.available_to_sell(product.id)

    # Should be 100 - 20 = 80
    assert available == Decimal("80.0")


def test_reserve_inventory(db_session: Session):
    """
    Test creating inventory reservation.
    """
    from app.services.inventory import InventoryService

    # Create product
    product = Product(sku="TEST-002", name="Test Product", base_unit="KG")
    db_session.add(product)
    db_session.flush()

    # Create inventory lot
    lot = InventoryLot(
        product_id=product.id,
        lot_code="LOT-002",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(),
        is_active=True,
    )
    db_session.add(lot)
    db_session.flush()

    # Reserve inventory
    inventory = InventoryService(db_session)
    reservation = inventory.reserve_inventory(
        product_id=product.id,
        qty_kg=Decimal("30.0"),
        source="shopify",
        reference_id="ORDER-002",
    )
    db_session.commit()

    # Verify reservation
    assert reservation.product_id == product.id
    assert reservation.qty_canonical == Decimal("30.0")
    assert reservation.source == "shopify"
    assert reservation.reference_id == "ORDER-002"
    assert reservation.status == "ACTIVE"


def test_commit_reservation(db_session: Session):
    """
    Test committing a reservation (FIFO consumption).
    """
    from app.services.inventory import InventoryService

    # Create product
    product = Product(sku="TEST-003", name="Test Product", base_unit="KG")
    db_session.add(product)
    db_session.flush()

    # Create multiple lots (FIFO order)
    lot1 = InventoryLot(
        product_id=product.id,
        lot_code="LOT-003A",
        quantity_kg=Decimal("50.0"),
        unit_cost=Decimal("10.0"),
        received_at=datetime(2024, 1, 1),
        is_active=True,
    )
    lot2 = InventoryLot(
        product_id=product.id,
        lot_code="LOT-003B",
        quantity_kg=Decimal("50.0"),
        unit_cost=Decimal("12.0"),
        received_at=datetime(2024, 1, 10),
        is_active=True,
    )
    db_session.add_all([lot1, lot2])
    db_session.flush()

    # Create reservation
    inventory = InventoryService(db_session)
    reservation = inventory.reserve_inventory(
        product_id=product.id,
        qty_kg=Decimal("30.0"),
        source="shopify",
        reference_id="ORDER-003",
    )
    db_session.flush()

    # Commit reservation
    inventory.commit_reservation(reservation.id)
    db_session.commit()

    # Verify lots were consumed via FIFO
    db_session.refresh(lot1)
    db_session.refresh(lot2)

    # lot1 should be partially consumed (30 out of 50)
    assert lot1.quantity_kg == Decimal("20.0")
    # lot2 should be untouched
    assert lot2.quantity_kg == Decimal("50.0")


def test_release_reservation(db_session: Session):
    """
    Test releasing a reservation.
    """
    from app.services.inventory import InventoryService

    # Create product
    product = Product(sku="TEST-004", name="Test", base_unit="KG")
    db_session.add(product)
    db_session.flush()

    # Create reservation
    inventory = InventoryService(db_session)
    reservation = inventory.reserve_inventory(
        product_id=product.id,
        qty_kg=Decimal("25.0"),
        source="shopify",
        reference_id="ORDER-004",
    )
    db_session.commit()

    # Release reservation
    inventory.release_reservation(reservation.id)
    db_session.commit()

    # Verify status changed
    db_session.refresh(reservation)
    assert reservation.status == "RELEASED"


@patch("app.services.shopify_sync.ShopifyClient")
def test_push_inventory_no_mapping(mock_client, db_session: Session):
    """
    Test push inventory fails without channel mapping.
    """
    svc = ShopifySyncService(db_session)

    # Try to push product without mapping
    result = svc.push_inventory("nonexistent-product-id")

    assert not result.get("ok")
    assert "no_shopify_mapping" in result.get("error")


def test_shopify_webhook_order_create(db_session: Session):
    """
    Test processing Shopify order webhook.
    """
    # Create products
    product1 = Product(sku="SHOP-001", name="Product 1", base_unit="KG")
    product2 = Product(sku="SHOP-002", name="Product 2", base_unit="KG")
    db_session.add_all([product1, product2])
    db_session.flush()

    # Create channel links
    link1 = ProductChannelLink(
        product_id=product1.id,
        channel="shopify",
        shopify_variant_id="v1",
        shopify_location_id="loc1",
    )
    link2 = ProductChannelLink(
        product_id=product2.id,
        channel="shopify",
        shopify_variant_id="v2",
        shopify_location_id="loc1",
    )
    db_session.add_all([link1, link2])
    db_session.flush()

    # Create inventory
    lot1 = InventoryLot(
        product_id=product1.id,
        lot_code="L1",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("10.0"),
        received_at=datetime.utcnow(),
        is_active=True,
    )
    lot2 = InventoryLot(
        product_id=product2.id,
        lot_code="L2",
        quantity_kg=Decimal("100.0"),
        unit_cost=Decimal("15.0"),
        received_at=datetime.utcnow(),
        is_active=True,
    )
    db_session.add_all([lot1, lot2])
    db_session.commit()

    # Mock Shopify webhook payload
    payload = {
        "id": "123456",
        "line_items": [
            {"variant_id": "v1", "quantity": 5},
            {"variant_id": "v2", "quantity": 3},
        ],
    }

    svc = ShopifySyncService(db_session)
    result = svc.apply_shopify_order(payload)

    # Verify reservations were created
    assert result["ok"]
    assert len(result["reservations"]) == 2

    # Verify reservations exist in DB
    reservations = (
        db_session.query(InventoryReservation)
        .filter(
            InventoryReservation.reference_id == "123456",
            InventoryReservation.status == "ACTIVE",
        )
        .all()
    )

    assert len(reservations) == 2
