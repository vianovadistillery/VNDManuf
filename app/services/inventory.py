"""
Inventory Service - Core inventory operations with FIFO and reservations.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.adapters.db.models import InventoryLot, InventoryTxn, Product
from app.adapters.db.models_assemblies_shopify import InventoryReservation
from app.domain.rules import fifo_issue, FifoIssue, round_quantity


class InventoryService:
    """
    Service for inventory operations: FIFO consumption, reservations, and lot management.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def available_to_sell(self, product_id: str) -> Decimal:
        """
        Calculate available quantity: on_hand - reserved - quarantine.
        
        Args:
            product_id: Product ID
            
        Returns:
            Available quantity in kg
        """
        # Get on-hand quantity from all active lots
        lots = self.db.query(InventoryLot).filter(
            InventoryLot.product_id == product_id,
            InventoryLot.is_active == True
        ).all()
        
        on_hand = sum(lot.quantity_kg for lot in lots)
        
        # Get reserved quantity from active reservations
        reservations = self.db.query(InventoryReservation).filter(
            InventoryReservation.product_id == product_id,
            InventoryReservation.status == "ACTIVE"
        ).all()
        
        reserved = sum(res.qty_canonical for res in reservations)
        
        # Quarantine not yet implemented (will be lot flag)
        available = on_hand - reserved
        
        return round_quantity(available)
    
    def get_lots_fifo(self, product_id: str) -> List[InventoryLot]:
        """
        Get inventory lots for a product ordered by FIFO (oldest first).
        
        Args:
            product_id: Product ID
            
        Returns:
            List of lots ordered by received_at
        """
        lots = self.db.query(InventoryLot).filter(
            InventoryLot.product_id == product_id,
            InventoryLot.is_active == True
        ).order_by(InventoryLot.received_at.asc()).all()
        
        return lots
    
    def consume_lots_fifo(
        self,
        product_id: str,
        qty_kg: Decimal,
        reason: str,
        ref_type: str,
        ref_id: Optional[str],
        notes: Optional[str] = None
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
        issues = fifo_issue(lots, qty_kg, override_negative=False)
        
        # Update lots and write transactions
        for issue in issues:
            lot = next(lot for lot in lots if lot.id == issue.lot_id)
            lot.quantity_kg = issue.remaining_quantity_kg
            
            # Write transaction
            self.write_inventory_txn(
                lot_id=lot.id,
                txn_type="ISSUE",
                qty_kg=-abs(issue.quantity_kg),  # Negative for issues
                unit_cost=issue.unit_cost,
                ref_type=ref_type,
                ref_id=ref_id,
                notes=notes or reason
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
        expires_at: Optional[datetime] = None
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
            is_active=True
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
            notes=f"Created lot {lot_code}"
        )
        
        return lot
    
    def write_inventory_txn(
        self,
        lot_id: str,
        txn_type: str,
        qty_kg: Decimal,
        unit_cost: Optional[Decimal],
        ref_type: Optional[str],
        ref_id: Optional[str],
        notes: Optional[str]
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
        txn = InventoryTxn(
            lot_id=lot_id,
            transaction_type=txn_type,
            quantity_kg=round_quantity(qty_kg),
            unit_cost=unit_cost,
            reference_type=ref_type,
            reference_id=ref_id,
            notes=notes,
            created_at=datetime.utcnow()
        )
        
        self.db.add(txn)
        return txn
    
    def reserve_inventory(
        self,
        product_id: str,
        qty_kg: Decimal,
        source: str,
        reference_id: str
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
        existing = self.db.query(InventoryReservation).filter(
            InventoryReservation.product_id == product_id,
            InventoryReservation.source == source,
            InventoryReservation.reference_id == reference_id,
            InventoryReservation.status == "ACTIVE"
        ).first()
        
        if existing:
            raise ValueError(f"Reservation already exists for reference {reference_id}")
        
        reservation = InventoryReservation(
            product_id=product_id,
            qty_canonical=round_quantity(qty_kg),
            source=source,
            reference_id=reference_id,
            status="ACTIVE"
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
        reservation = self.db.query(InventoryReservation).filter(
            InventoryReservation.id == reservation_id
        ).first()
        
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        if reservation.status != "ACTIVE":
            raise ValueError(f"Reservation {reservation_id} is not active")
        
        # Consume via FIFO
        self.consume_lots_fifo(
            product_id=reservation.product_id,
            qty_kg=reservation.qty_canonical,
            reason="FULFILL_ORDER",
            ref_type=reservation.source.upper(),
            ref_id=reservation.reference_id,
            notes=f"Committed reservation {reservation_id}"
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
        reservation = self.db.query(InventoryReservation).filter(
            InventoryReservation.id == reservation_id
        ).first()
        
        if not reservation:
            raise ValueError(f"Reservation {reservation_id} not found")
        
        if reservation.status != "ACTIVE":
            raise ValueError(f"Reservation {reservation_id} is not active")
        
        # Mark as released
        reservation.status = "RELEASED"
        reservation.updated_at = datetime.utcnow()
        self.db.flush()
