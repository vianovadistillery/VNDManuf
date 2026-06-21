"""
Inventory Service - Core inventory operations with FIFO and reservations.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.orm import Session

from app.adapters.db.models import InventoryLot, InventoryTxn, Product
from app.adapters.db.models_assemblies_shopify import InventoryReservation
from app.domain.inventory_uom import format_stock, inventory_uom_for_product
from app.domain.rules import (
    FifoIssue,
    fifo_issue,
    fifo_peek_cost,
    round_money,
    round_quantity,
)

WRITE_OFF_REASONS = frozenset({"DAMAGED", "LOST", "SHRINKAGE", "OTHER"})


class InventoryService:
    """
    Service for inventory operations: FIFO consumption, reservations, and lot management.
    """

    def __init__(self, db: Session):
        self.db = db

    def get_inventory_uom(self, product_id: str) -> str:
        product = self.db.get(Product, product_id)
        return inventory_uom_for_product(product)

    def available_to_sell(self, product_id: str) -> Decimal:
        """
        Calculate available quantity in the product's inventory UOM:
        on_hand - reserved.
        """
        # Get on-hand quantity from all active lots
        lots = (
            self.db.query(InventoryLot)
            .filter(
                InventoryLot.product_id == product_id, InventoryLot.is_active.is_(True)
            )
            .all()
        )

        on_hand = sum(lot.quantity_kg for lot in lots)

        # Get reserved quantity from active reservations
        reservations = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.product_id == product_id,
                InventoryReservation.status == "ACTIVE",
            )
            .all()
        )

        reserved = sum(res.qty_canonical for res in reservations)

        # Quarantine not yet implemented (will be lot flag)
        available = on_hand - reserved

        return round_quantity(available)

    def get_stock_on_hand(self, product_id: str) -> Decimal:
        """Sum active lot quantities in the product's inventory unit."""
        lots = self.get_lots_fifo(product_id)
        return round_quantity(sum(lot.quantity_kg for lot in lots))

    def stock_on_hand_payload(self, product_id: str) -> Dict[str, Any]:
        """Stock on hand with unit for API/UI."""
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")
        qty = self.get_stock_on_hand(product_id)
        unit = inventory_uom_for_product(product)
        return {
            "product_id": product_id,
            "product_sku": product.sku,
            "product_name": product.name,
            "stock_on_hand": float(qty),
            "inventory_unit": unit,
            "stock_on_hand_kg": float(qty),
            "stock_display": format_stock(qty, unit),
        }

    def get_lots_fifo(self, product_id: str) -> List[InventoryLot]:
        """
        Get inventory lots for a product ordered by FIFO (oldest first).

        Args:
            product_id: Product ID

        Returns:
            List of lots ordered by received_at
        """
        lots = (
            self.db.query(InventoryLot)
            .filter(
                InventoryLot.product_id == product_id, InventoryLot.is_active.is_(True)
            )
            .order_by(InventoryLot.received_at.asc())
            .all()
        )

        return lots

    def _get_or_create_negative_lot(self, product_id: str) -> InventoryLot:
        """Get or create a placeholder lot used to track negative inventory."""
        lot = (
            self.db.query(InventoryLot)
            .filter(
                InventoryLot.product_id == product_id,
                InventoryLot.lot_code == "__AUTO_NEGATIVE__",
                InventoryLot.is_active.is_(True),
            )
            .first()
        )

        if not lot:
            lot = InventoryLot(
                product_id=product_id,
                lot_code="__AUTO_NEGATIVE__",
                quantity_kg=round_quantity(Decimal("0")),
                unit_cost=Decimal("0"),
                received_at=datetime.utcnow(),
                is_active=True,
            )
            self.db.add(lot)
            self.db.flush()

        return lot

    def consume_lots_fifo(
        self,
        product_id: str,
        qty_kg: Decimal,
        reason: str,
        ref_type: str,
        ref_id: Optional[str],
        notes: Optional[str] = None,
        allow_negative: bool = False,
        txn_type: str = "ISSUE",
    ) -> List[FifoIssue]:
        """
        Consume inventory using FIFO logic.

        Args:
            product_id: Product ID
            qty_kg: Quantity to consume in kg
            reason: Reason for consumption
            ref_type: Reference type (e.g., "ASSEMBLE", "SALES_ORDER")
            ref_id: Reference ID
            notes: Optional notes

        Returns:
            List of FifoIssue results

        Raises:
            ValueError: If insufficient stock
        """
        lots = self.get_lots_fifo(product_id)

        # Use domain FIFO logic
        issues = fifo_issue(lots, qty_kg, override_negative=allow_negative)

        issued_total = sum(issue.quantity_kg for issue in issues)
        if allow_negative and issued_total < qty_kg:
            deficit = round_quantity(qty_kg - issued_total)
            if deficit > 0:
                negative_lot = self._get_or_create_negative_lot(product_id)
                if negative_lot not in lots:
                    lots.append(negative_lot)

                starting_qty = negative_lot.quantity_kg or Decimal("0")
                remaining_qty = round_quantity(starting_qty - deficit)
                issues.append(
                    FifoIssue(
                        lot_id=negative_lot.id,
                        quantity_kg=deficit,
                        unit_cost=negative_lot.unit_cost or Decimal("0"),
                        remaining_quantity_kg=remaining_qty,
                    )
                )

        # Update lots and write transactions
        for issue in issues:
            lot = next(lot for lot in lots if lot.id == issue.lot_id)
            lot.quantity_kg = issue.remaining_quantity_kg

            # Write transaction
            self.write_inventory_txn(
                lot_id=lot.id,
                txn_type=txn_type,
                qty_kg=-abs(issue.quantity_kg),  # Negative for issues
                unit_cost=issue.unit_cost,
                ref_type=ref_type,
                ref_id=ref_id,
                notes=notes or reason,
            )

        self.db.flush()
        return issues

    def add_lot(
        self,
        product_id: str,
        lot_code: str,
        qty_kg: Decimal,
        unit_cost: Decimal,
        received_at: Optional[datetime] = None,
        expires_at: Optional[datetime] = None,
    ) -> InventoryLot:
        """
        Create a new inventory lot.

        Args:
            product_id: Product ID
            lot_code: Lot code
            qty_kg: Quantity in kg
            unit_cost: Cost per kg
            received_at: Receipt date (defaults to now)
            expires_at: Optional expiry date

        Returns:
            Created InventoryLot
        """
        lot = InventoryLot(
            product_id=product_id,
            lot_code=lot_code,
            quantity_kg=round_quantity(qty_kg),
            unit_cost=unit_cost,
            received_at=received_at or datetime.utcnow(),
            expires_at=expires_at,
            is_active=True,
        )

        self.db.add(lot)
        self.db.flush()

        # Write RECEIPT transaction
        self.write_inventory_txn(
            lot_id=lot.id,
            txn_type="RECEIPT",
            qty_kg=qty_kg,
            unit_cost=unit_cost,
            ref_type="LOT_CREATE",
            ref_id=None,
            notes=f"Created lot {lot_code}",
        )

        return lot

    def _default_unit_cost(self, product_id: str) -> Decimal:
        product = self.db.get(Product, product_id)
        if not product:
            return Decimal("0")
        lots = self.get_lots_fifo(product_id)
        peek = fifo_peek_cost(lots)
        if peek is not None and peek > 0:
            return peek
        for attr in (
            "usage_cost_ex_gst",
            "purchase_cost_ex_gst",
            "usage_cost",
            "standard_cost",
        ):
            val = getattr(product, attr, None)
            if val is not None and Decimal(str(val)) > 0:
                return Decimal(str(val))
        return Decimal("0")

    def get_inventory_summary(self, product_id: str) -> Dict[str, Any]:
        """Return stock, costing, and lot summary for a product."""
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        lots = [
            lot
            for lot in self.get_lots_fifo(product_id)
            if lot.lot_code != "__AUTO_NEGATIVE__"
        ]
        soh = sum(lot.quantity_kg for lot in lots)
        soh = round_quantity(soh)
        inv_unit = inventory_uom_for_product(product)

        fifo_cost = fifo_peek_cost(lots) or Decimal("0")
        if soh > 0:
            total_value = sum(
                lot.quantity_kg * (lot.unit_cost or Decimal("0")) for lot in lots
            )
            avg_cost = round_money(total_value / soh)
            fifo_total = round_money(soh * fifo_cost) if fifo_cost else total_value
            cost_source = "FIFO" if fifo_cost else "AVERAGE"
        else:
            avg_cost = self._default_unit_cost(product_id)
            total_value = Decimal("0")
            fifo_total = Decimal("0")
            cost_source = "STANDARD" if avg_cost else "UNKNOWN"

        return {
            "product_id": product_id,
            "product_sku": product.sku,
            "product_name": product.name,
            "stock_on_hand": float(soh),
            "inventory_unit": inv_unit,
            "stock_on_hand_kg": float(soh),
            "stock_display": format_stock(soh, inv_unit),
            "fifo_cost_per_kg": float(fifo_cost or avg_cost),
            "fifo_total_value": float(fifo_total),
            "avg_cost_per_kg": float(avg_cost),
            "avg_total_value": float(total_value),
            "cost_source": cost_source,
            "has_estimate": False,
            "estimate_reason": None,
            "active_lots_count": len(lots),
        }

    def set_product_count(
        self,
        product_id: str,
        target_qty_kg: Decimal,
        ref_type: str = "STOCKTAKE",
        ref_id: Optional[str] = None,
        notes: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        allow_negative: bool = False,
    ) -> Decimal:
        """Set total product SOH to target quantity (inventory unit). Returns variance."""
        product = self.db.get(Product, product_id)
        inv_unit = inventory_uom_for_product(product)
        current = self.get_stock_on_hand(product_id)
        variance = round_quantity(target_qty_kg - current)
        if variance == 0:
            return Decimal("0")

        txn_type = "STOCKTAKE" if ref_type == "STOCKTAKE" else "ADJUSTMENT"
        if variance > 0:
            cost = (
                unit_cost
                if unit_cost is not None
                else self._default_unit_cost(product_id)
            )
            lot_code = f"{ref_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
            lot = self.add_lot(product_id, lot_code, variance, cost)
            if lot.transactions:
                txn = lot.transactions[-1]
                txn.transaction_type = txn_type
                txn.reference_type = ref_type
                txn.reference_id = ref_id
                txn.notes = notes or f"Set count to {target_qty_kg} {inv_unit}"
        else:
            allow = allow_negative or bool(
                getattr(product, "allow_negative_inventory", False)
                if product
                else False
            )
            self.consume_lots_fifo(
                product_id=product_id,
                qty_kg=abs(variance),
                reason=notes or f"Set count to {target_qty_kg} {inv_unit}",
                ref_type=ref_type,
                ref_id=ref_id,
                notes=notes,
                allow_negative=allow,
                txn_type=txn_type,
            )
        self.db.flush()
        return variance

    def adjust_inventory(
        self,
        product_id: str,
        adjustment_type: str,
        quantity_kg: Decimal,
        lot_id: Optional[str] = None,
        lot_code: Optional[str] = None,
        unit_cost: Optional[Decimal] = None,
        reference_type: Optional[str] = None,
        reference_id: Optional[str] = None,
        notes: Optional[str] = None,
        allow_negative: bool = False,
    ) -> Dict[str, Any]:
        """Apply a manual inventory adjustment and return result metadata."""
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        if adjustment_type == "INCREASE" and quantity_kg <= 0:
            raise ValueError("Increase quantity must be greater than zero")
        if adjustment_type == "DECREASE" and quantity_kg <= 0:
            raise ValueError("Decrease quantity must be greater than zero")

        ref_type = reference_type or "MANUAL"
        allow = allow_negative or bool(
            getattr(product, "allow_negative_inventory", False)
        )

        if adjustment_type == "SET_COUNT" and not lot_id:
            variance = self.set_product_count(
                product_id=product_id,
                target_qty_kg=quantity_kg,
                ref_type=ref_type,
                ref_id=reference_id,
                notes=notes,
                unit_cost=unit_cost,
                allow_negative=allow,
            )
            return {
                "product_id": product_id,
                "lot_id": None,
                "adjustment_type": adjustment_type,
                "quantity_delta_kg": variance,
                "new_quantity_kg": self.get_stock_on_hand(product_id),
                "inventory_unit": inventory_uom_for_product(product),
                "unit_cost": unit_cost or self._default_unit_cost(product_id),
                "notes": notes,
                "reference_type": ref_type,
                "reference_id": reference_id,
            }

        if adjustment_type == "DECREASE" and not lot_id:
            self.consume_lots_fifo(
                product_id=product_id,
                qty_kg=quantity_kg,
                reason=notes or "Manual decrease",
                ref_type=ref_type,
                ref_id=reference_id,
                notes=notes,
                allow_negative=allow,
                txn_type="ADJUSTMENT",
            )
            return {
                "product_id": product_id,
                "lot_id": None,
                "adjustment_type": adjustment_type,
                "quantity_delta_kg": -abs(quantity_kg),
                "new_quantity_kg": self.get_stock_on_hand(product_id),
                "unit_cost": unit_cost or self._default_unit_cost(product_id),
                "notes": notes,
                "reference_type": ref_type,
                "reference_id": reference_id,
            }

        if not lot_id and adjustment_type == "INCREASE":
            cost = (
                unit_cost
                if unit_cost is not None
                else self._default_unit_cost(product_id)
            )
            code = (
                lot_code.strip()
                if lot_code and lot_code.strip()
                else f"ADJ-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
            )
            lot = self.add_lot(product_id, code, quantity_kg, cost)
            if lot.transactions:
                txn = lot.transactions[-1]
                txn.transaction_type = "ADJUSTMENT"
                txn.reference_type = ref_type
                txn.reference_id = reference_id
                txn.notes = notes or f"Manual increase lot {code}"
            self.db.flush()
            return {
                "product_id": product_id,
                "lot_id": lot.id,
                "adjustment_type": adjustment_type,
                "quantity_delta_kg": quantity_kg,
                "new_quantity_kg": lot.quantity_kg,
                "unit_cost": cost,
                "notes": notes,
                "reference_type": ref_type,
                "reference_id": reference_id,
            }

        if not lot_id:
            raise ValueError(
                f"lot_id is required for adjustment type {adjustment_type}"
            )

        lot = self.db.get(InventoryLot, lot_id)
        if not lot:
            raise ValueError(f"Lot {lot_id} not found")
        if lot.product_id != product_id:
            raise ValueError("Lot does not belong to specified product")

        current_qty = lot.quantity_kg or Decimal("0")
        if adjustment_type == "SET_COUNT":
            delta_kg = quantity_kg - current_qty
            new_qty = quantity_kg
        elif adjustment_type == "INCREASE":
            delta_kg = quantity_kg
            new_qty = current_qty + quantity_kg
        elif adjustment_type == "DECREASE":
            delta_kg = -abs(quantity_kg)
            new_qty = current_qty - abs(quantity_kg)
        else:
            raise ValueError(f"Invalid adjustment type: {adjustment_type}")

        if new_qty < 0 and not allow:
            raise ValueError("Insufficient stock for decrease on selected lot")

        lot.quantity_kg = round_quantity(new_qty)
        if unit_cost is not None:
            if lot.original_unit_cost is None:
                lot.original_unit_cost = lot.unit_cost or unit_cost
            lot.current_unit_cost = unit_cost
            lot.unit_cost = unit_cost

        txn = self.write_inventory_txn(
            lot_id=lot.id,
            txn_type="ADJUSTMENT",
            qty_kg=delta_kg,
            unit_cost=unit_cost or lot.unit_cost or lot.current_unit_cost,
            ref_type=ref_type,
            ref_id=reference_id,
            notes=notes,
            cost_source="override" if unit_cost else None,
        )
        self.db.flush()
        return {
            "product_id": product_id,
            "lot_id": lot.id,
            "adjustment_type": adjustment_type,
            "quantity_delta_kg": delta_kg,
            "new_quantity_kg": lot.quantity_kg,
            "unit_cost": unit_cost or lot.unit_cost or lot.current_unit_cost,
            "notes": notes,
            "reference_type": ref_type,
            "reference_id": reference_id,
            "transaction_id": str(txn.id),
        }

    def write_off(
        self,
        product_id: str,
        quantity_kg: Decimal,
        reason: str,
        lot_id: Optional[str] = None,
        notes: Optional[str] = None,
        reference_id: Optional[str] = None,
        allow_negative: bool = False,
    ) -> Dict[str, Any]:
        """Write off damaged, lost, or shrinkage stock."""
        reason_upper = (reason or "OTHER").upper()
        if reason_upper not in WRITE_OFF_REASONS:
            raise ValueError(
                f"Invalid write-off reason: {reason}. "
                f"Must be one of: {', '.join(sorted(WRITE_OFF_REASONS))}"
            )

        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        ref_type = f"WRITE_OFF_{reason_upper}"
        note_text = notes or f"Write-off: {reason_upper}"
        allow = allow_negative or bool(
            getattr(product, "allow_negative_inventory", False)
        )
        qty = abs(quantity_kg)

        if lot_id:
            result = self.adjust_inventory(
                product_id=product_id,
                adjustment_type="DECREASE",
                quantity_kg=qty,
                lot_id=lot_id,
                reference_type=ref_type,
                reference_id=reference_id,
                notes=note_text,
                allow_negative=allow,
            )
            result["write_off_reason"] = reason_upper
            return result

        self.consume_lots_fifo(
            product_id=product_id,
            qty_kg=qty,
            reason=note_text,
            ref_type=ref_type,
            ref_id=reference_id,
            notes=note_text,
            allow_negative=allow,
            txn_type="WRITE_OFF",
        )
        self.db.flush()
        return {
            "product_id": product_id,
            "lot_id": None,
            "write_off_reason": reason_upper,
            "quantity_delta_kg": -qty,
            "new_quantity_kg": self.get_stock_on_hand(product_id),
            "notes": note_text,
            "reference_type": ref_type,
            "reference_id": reference_id,
        }

    def write_inventory_txn(
        self,
        lot_id: str,
        txn_type: str,
        qty_kg: Decimal,
        unit_cost: Optional[Decimal],
        ref_type: Optional[str],
        ref_id: Optional[str],
        notes: Optional[str],
        cost_source: Optional[str] = None,
    ) -> InventoryTxn:
        """
        Write an inventory transaction (audit trail).

        Args:
            lot_id: Lot ID
            txn_type: Transaction type (RECEIPT, ISSUE, ADJUSTMENT)
            qty_kg: Quantity in kg
            unit_cost: Cost per kg
            ref_type: Reference type
            ref_id: Reference ID
            notes: Notes

        Returns:
            Created InventoryTxn
        """
        qty_rounded = round_quantity(qty_kg)
        extended = None
        if unit_cost is not None:
            extended = round_money(abs(qty_rounded) * unit_cost)

        txn = InventoryTxn(
            lot_id=lot_id,
            transaction_type=txn_type,
            quantity_kg=qty_rounded,
            unit_cost=unit_cost,
            extended_cost=extended,
            cost_source=cost_source,
            reference_type=ref_type,
            reference_id=ref_id,
            notes=notes,
            created_at=datetime.utcnow(),
        )

        self.db.add(txn)
        return txn

    def reserve_inventory(
        self, product_id: str, qty_kg: Decimal, source: str, reference_id: str
    ) -> InventoryReservation:
        """
        Reserve inventory for an order (prevents double-booking).

        Args:
            product_id: Product ID
            qty_kg: Quantity to reserve in kg
            source: Source (e.g., "shopify", "internal")
            reference_id: Reference ID (e.g., order ID)

        Returns:
            Created InventoryReservation

        Raises:
            ValueError: If already reserved for this reference
        """
        # Check for existing reservation
        existing = (
            self.db.query(InventoryReservation)
            .filter(
                InventoryReservation.product_id == product_id,
                InventoryReservation.source == source,
                InventoryReservation.reference_id == reference_id,
                InventoryReservation.status == "ACTIVE",
            )
            .first()
        )

        if existing:
            raise ValueError(f"Reservation already exists for reference {reference_id}")

        reservation = InventoryReservation(
            product_id=product_id,
            qty_canonical=round_quantity(qty_kg),
            source=source,
            reference_id=reference_id,
            status="ACTIVE",
        )

        self.db.add(reservation)
        self.db.flush()

        return reservation

    def commit_reservation(self, reservation_id: str) -> None:
        """
        Commit a reservation (convert to actual consumption via FIFO).

        Args:
            reservation_id: Reservation ID

        Raises:
            ValueError: If reservation not found or not active
        """
        reservation = (
            self.db.query(InventoryReservation)
            .filter(InventoryReservation.id == reservation_id)
            .first()
        )

        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        if reservation.status != "ACTIVE":
            raise ValueError(f"Reservation {reservation_id} is not active")

        # Consume via FIFO
        product = self.db.get(Product, reservation.product_id)
        allow_negative = bool(
            getattr(product, "allow_negative_inventory", False) if product else False
        )

        self.consume_lots_fifo(
            product_id=reservation.product_id,
            qty_kg=reservation.qty_canonical,
            reason="FULFILL_ORDER",
            ref_type=reservation.source.upper(),
            ref_id=reservation.reference_id,
            notes=f"Committed reservation {reservation_id}",
            allow_negative=allow_negative,
        )

        # Mark as committed
        reservation.status = "COMMITTED"
        reservation.updated_at = datetime.utcnow()
        self.db.flush()

    def release_reservation(self, reservation_id: str) -> None:
        """
        Release a reservation (return to available).

        Args:
            reservation_id: Reservation ID

        Raises:
            ValueError: If reservation not found or not active
        """
        reservation = (
            self.db.query(InventoryReservation)
            .filter(InventoryReservation.id == reservation_id)
            .first()
        )

        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")

        if reservation.status != "ACTIVE":
            raise ValueError(f"Reservation {reservation_id} is not active")

        # Mark as released
        reservation.status = "RELEASED"
        reservation.updated_at = datetime.utcnow()
        self.db.flush()
