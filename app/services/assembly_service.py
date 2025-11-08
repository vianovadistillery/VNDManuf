from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.adapters.db.models import Product
from app.adapters.db.models_assemblies_shopify import Assembly, AssemblyDirection
from app.domain.rules import round_quantity
from app.services.inventory import InventoryService


class AssemblyService:
    """
    Encapsulates assemble/disassemble operations.
    All quantities here are in canonical units (e.g., kg for liquids; counts for packages if canonicalized).
    """

    def __init__(self, db: Session):
        self.db = db
        self.inventory = InventoryService(db)

    def assemble(
        self, parent_product_id: str, parent_qty: Decimal, reason: str = "ASSEMBLE"
    ):
        """
        Make parent product from children according to Assembly rows where parent=parent_product_id.
        1) For each child row: consume child stock = parent_qty * ratio (+loss_factor handling).
        2) Add parent stock (lot).
        3) Write inventory transactions.

        Returns:
            Dict with consumed children and produced parent information
        """
        # Get all assembly definitions for this parent
        assemblies = (
            self.db.query(Assembly)
            .filter(
                Assembly.parent_product_id == parent_product_id,
                Assembly.direction == AssemblyDirection.MAKE_FROM_CHILDREN.value,
            )
            .all()
        )

        if not assemblies:
            raise ValueError(
                f"No assembly definitions found for product {parent_product_id}"
            )

        consumed_children = []
        total_parent_cost = Decimal("0")

        # Process each child assembly
        for assembly in assemblies:
            # Calculate child quantity needed with loss factor
            child_need = (
                parent_qty * assembly.ratio * (Decimal("1") + assembly.loss_factor)
            )
            child_need = round_quantity(child_need)

            # Consume child inventory via FIFO
            child_product = self.db.get(Product, assembly.child_product_id)
            allow_negative = bool(
                getattr(child_product, "allow_negative_inventory", False)
                if child_product
                else False
            )
            issues = self.inventory.consume_lots_fifo(
                product_id=assembly.child_product_id,
                qty_kg=child_need,
                reason=reason,
                ref_type="ASSEMBLE",
                ref_id=parent_product_id,
                notes=f"Assembly: {reason}",
                allow_negative=allow_negative,
            )

            # Calculate total cost consumed from this child
            child_cost = sum(issue.quantity_kg * issue.unit_cost for issue in issues)
            total_parent_cost += child_cost

            consumed_children.append(
                {
                    "child_product_id": assembly.child_product_id,
                    "ratio": assembly.ratio,
                    "loss_factor": assembly.loss_factor,
                    "qty_consumed": child_need,
                    "cost": child_cost,
                    "issues": issues,
                }
            )

        # Create parent lot
        parent_unit_cost = (
            total_parent_cost / parent_qty if parent_qty > 0 else Decimal("0")
        )
        lot_code = f"ASSM-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

        parent_lot = self.inventory.add_lot(
            product_id=parent_product_id,
            lot_code=lot_code,
            qty_kg=parent_qty,
            unit_cost=round_quantity(parent_unit_cost),
            received_at=datetime.utcnow(),
        )

        return {
            "consumed": consumed_children,
            "produced": {
                "product_id": parent_product_id,
                "quantity_kg": parent_qty,
                "unit_cost": parent_unit_cost,
                "total_cost": total_parent_cost,
                "lot_id": parent_lot.id,
                "lot_code": lot_code,
            },
        }

    def disassemble(
        self, parent_product_id: str, parent_qty: Decimal, reason: str = "DISASSEMBLE"
    ):
        """
        Break parent product into children (use ratio; subtract loss_factor).

        Returns:
            Dict with consumed parent and produced children information
        """
        # Get all assembly definitions (reverse direction)
        assemblies = (
            self.db.query(Assembly)
            .filter(Assembly.parent_product_id == parent_product_id)
            .all()
        )

        if not assemblies:
            raise ValueError(
                f"No assembly definitions found for product {parent_product_id}"
            )

        # Consume parent via FIFO
        parent_product = self.db.get(Product, parent_product_id)
        allow_negative = bool(
            getattr(parent_product, "allow_negative_inventory", False)
            if parent_product
            else False
        )
        parent_issues = self.inventory.consume_lots_fifo(
            product_id=parent_product_id,
            qty_kg=parent_qty,
            reason=reason,
            ref_type="DISASSEMBLE",
            ref_id=parent_product_id,
            notes=f"Disassembly: {reason}",
            allow_negative=allow_negative,
        )

        # Calculate parent cost
        parent_cost = sum(
            issue.quantity_kg * issue.unit_cost for issue in parent_issues
        )

        produced_children = []

        # Produce children with loss factor
        for assembly in assemblies:
            # Calculate child quantity produced (subtract loss factor)
            child_produced = (
                parent_qty * assembly.ratio * (Decimal("1") - assembly.loss_factor)
            )
            child_produced = round_quantity(child_produced)

            # Allocate cost proportionally
            child_cost = (
                parent_cost * assembly.ratio / sum(a.ratio for a in assemblies)
                if assemblies
                else Decimal("0")
            )
            child_unit_cost = (
                child_cost / child_produced if child_produced > 0 else Decimal("0")
            )

            # Create child lot
            lot_code = f"DISS-{assembly.child_product_id[:8]}-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"

            child_lot = self.inventory.add_lot(
                product_id=assembly.child_product_id,
                lot_code=lot_code,
                qty_kg=child_produced,
                unit_cost=round_quantity(child_unit_cost),
                received_at=datetime.utcnow(),
            )

            produced_children.append(
                {
                    "child_product_id": assembly.child_product_id,
                    "ratio": assembly.ratio,
                    "loss_factor": assembly.loss_factor,
                    "qty_produced": child_produced,
                    "cost": child_cost,
                    "lot_id": child_lot.id,
                    "lot_code": lot_code,
                }
            )

        return {
            "consumed": {
                "product_id": parent_product_id,
                "quantity_kg": parent_qty,
                "cost": parent_cost,
                "issues": parent_issues,
            },
            "produced": produced_children,
        }
