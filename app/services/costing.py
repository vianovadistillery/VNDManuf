# app/services/costing.py
"""Service for cost of goods (COGS) inspection, revaluation, and multi-level cost roll-up."""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.adapters.db.models import (
    AssemblyCostDependency,
    InventoryLot,
    InventoryTxn,
    Product,
    Revaluation,
)
from app.adapters.db.models_assemblies_shopify import Assembly as AssemblyModel
from app.domain.rules import CostSource, get_item_cost, round_money, round_quantity


class CostingService:
    """Service for COGS inspection, cost roll-up, and revaluation."""

    def __init__(self, db: Session):
        self.db = db

    def get_current_cost(self, product_id: str) -> Dict[str, Any]:
        """
        Get current cost for a product (latest available).

        Args:
            product_id: Product ID

        Returns:
            Dictionary with unit_cost, cost_source, has_estimate, estimate_reason
        """
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        return get_item_cost(product)

    def get_historical_cost(
        self, product_id: str, as_of_date: datetime
    ) -> Dict[str, Any]:
        """
        Get historical cost for a product as of a specific date.

        Args:
            product_id: Product ID
            as_of_date: Point-in-time date

        Returns:
            Dictionary with unit_cost, cost_source, has_estimate, estimate_reason
        """
        product = self.db.get(Product, product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        # Filter lots to those received before as_of_date
        lots = (
            self.db.query(InventoryLot)
            .filter(
                InventoryLot.product_id == product_id,
                InventoryLot.received_at <= as_of_date,
                InventoryLot.is_active.is_(True),
            )
            .all()
        )

        return get_item_cost(product, as_of_date=as_of_date, lots=lots)

    def build_bom_tree(
        self,
        item_id: str,
        as_of_date: Optional[datetime] = None,
        include_estimates: bool = True,
        level: int = 0,
        path: str = "",
        visited: Optional[set] = None,
    ) -> Dict[str, Any]:
        """
        Recursively build BOM cost tree with multi-level roll-up.

        Args:
            item_id: Product ID to build tree for
            as_of_date: Optional point-in-time date
            include_estimates: Whether to include estimated costs
            level: Current recursion level
            path: Current path in tree (for cycle detection)
            visited: Set of visited product IDs (for cycle detection)

        Returns:
            Dictionary with tree structure: level, sku, name, qty_per_parent, unit_cost,
            extended_cost, cost_source, has_estimate, estimate_reason, children
        """
        if visited is None:
            visited = set()

        product = self.db.get(Product, item_id)
        if not product:
            raise ValueError(f"Product {item_id} not found")

        # Cycle detection
        if item_id in visited:
            raise ValueError(f"Circular BOM detected at {product.sku} (path: {path})")
        visited.add(item_id)

        # Get active assemblies for this parent
        assemblies = self.db.query(AssemblyModel).filter(
            AssemblyModel.parent_product_id == item_id,
            AssemblyModel.is_active.is_(True),
        )

        # Apply effective date filter if provided
        if as_of_date:
            assemblies = assemblies.filter(
                or_(
                    AssemblyModel.effective_from.is_(None),
                    AssemblyModel.effective_from <= as_of_date,
                ),
                or_(
                    AssemblyModel.effective_to.is_(None),
                    AssemblyModel.effective_to >= as_of_date,
                ),
            )

        assemblies = assemblies.all()

        # Leaf node - get direct cost
        if not assemblies:
            visited.remove(item_id)

            if as_of_date:
                cost_info = self.get_historical_cost(item_id, as_of_date)
            else:
                cost_info = self.get_current_cost(item_id)

            return {
                "level": level,
                "sku": product.sku,
                "name": product.name,
                # Determine product type from capabilities for backward compatibility
                "product_type": (
                    "FINISHED"
                    if product.is_assemble
                    else "RAW"
                    if product.is_purchase
                    else "WIP"
                ),
                "qty_per_parent": Decimal("1"),
                "unit_cost": cost_info["unit_cost"],
                "extended_cost": cost_info["unit_cost"],
                "cost_source": cost_info["cost_source"],
                "has_estimate": cost_info["has_estimate"],
                "estimate_reason": cost_info.get("estimate_reason"),
                "children": [],
            }

        # Parent node - roll up from children
        children = []
        total_cost = Decimal("0")
        has_any_estimate = False
        estimate_sources = []

        for assembly in assemblies:
            child_tree = self.build_bom_tree(
                assembly.child_product_id,
                as_of_date,
                include_estimates,
                level + 1,
                f"{path} → {product.sku}" if path else product.sku,
                set(visited),  # Pass copy to children
            )

            # Calculate quantity needed with loss factor and yield
            loss_adjusted_ratio = assembly.ratio * (
                Decimal("1") + (assembly.loss_factor or Decimal("0"))
            )
            yield_factor = assembly.yield_factor or Decimal("1.0")
            qty_needed = loss_adjusted_ratio / yield_factor

            child_extended = child_tree["unit_cost"] * qty_needed

            children.append(
                {
                    **child_tree,
                    "qty_per_parent": round_quantity(qty_needed),
                    "extended_cost": round_money(child_extended),
                    "assembly_ratio": assembly.ratio,
                    "loss_factor": assembly.loss_factor or Decimal("0"),
                    "yield_factor": yield_factor,
                    "is_energy_or_overhead": assembly.is_energy_or_overhead or False,
                }
            )

            total_cost += child_extended

            if child_tree["has_estimate"]:
                has_any_estimate = True
                if child_tree.get("estimate_reason"):
                    estimate_sources.append(
                        f"{child_tree['sku']}: {child_tree['estimate_reason']}"
                    )

        visited.remove(item_id)

        # Determine cost source for parent
        if has_any_estimate:
            cost_source = CostSource.ESTIMATED.value
            estimate_reason = (
                "Contains estimated components: " + "; ".join(estimate_sources)
                if estimate_sources
                else "Contains estimated components"
            )
        elif all(
            child["cost_source"] == CostSource.FIFO_ACTUAL.value for child in children
        ):
            cost_source = CostSource.FIFO_ACTUAL.value
            estimate_reason = None
        else:
            cost_source = CostSource.STANDARD.value
            estimate_reason = None

        return {
            "level": level,
            "sku": product.sku,
            "name": product.name,
            # Determine product type from capabilities for backward compatibility
            "product_type": (
                "FINISHED"
                if product.is_assemble
                else "RAW"
                if product.is_purchase
                else "WIP"
            ),
            "qty_per_parent": Decimal("1"),
            "unit_cost": round_money(total_cost),
            "extended_cost": round_money(total_cost),
            "cost_source": cost_source,
            "has_estimate": has_any_estimate,
            "estimate_reason": estimate_reason,
            "children": children,
        }

    def inspect_cogs(
        self,
        item_id: str,
        as_of_date: Optional[datetime] = None,
        include_estimates: bool = True,
    ) -> Dict[str, Any]:
        """
        Inspect cost of goods with multi-level breakdown, estimate flags, and point-in-time support.

        Args:
            item_id: Product ID to inspect
            as_of_date: Optional point-in-time date for historical costing
            include_estimates: Whether to include items with estimated costs

        Returns:
            Dictionary with item info, unit_cost, cost_source, has_estimate, and breakdown tree
        """
        product = self.db.get(Product, item_id)
        if not product:
            raise ValueError(f"Product {item_id} not found")

        # Get current or point-in-time cost (not used in BOM tree but available for future use)
        # if as_of_date:
        #     cost_data = self.get_historical_cost(item_id, as_of_date)
        # else:
        #     cost_data = self.get_current_cost(item_id)

        # Build BOM tree recursively
        tree = self.build_bom_tree(item_id, as_of_date, include_estimates)

        return {
            "item_id": item_id,
            "sku": product.sku,
            "name": product.name,
            # Determine product type from capabilities for backward compatibility
            "product_type": (
                "FINISHED"
                if product.is_assemble
                else "RAW"
                if product.is_purchase
                else "WIP"
            ),
            "unit_cost": tree["unit_cost"],
            "cost_source": tree["cost_source"],
            "has_estimate": tree["has_estimate"],
            "estimate_reason": tree.get("estimate_reason"),
            "breakdown": tree,
        }

    def revalue_lot(
        self,
        lot_id: str,
        new_unit_cost: Decimal,
        reason: str,
        revalued_by: str,
        propagate: bool = True,
    ) -> Revaluation:
        """
        Revalue a lot and optionally propagate to downstream assemblies.

        Args:
            lot_id: Lot ID to revalue
            new_unit_cost: New unit cost
            reason: Reason for revaluation
            revalued_by: User who performed revaluation
            propagate: Whether to propagate revaluation to downstream assemblies

        Returns:
            Revaluation record
        """
        lot = self.db.get(InventoryLot, lot_id)
        if not lot:
            raise ValueError(f"Lot {lot_id} not found")

        old_cost = (
            lot.current_unit_cost
            or lot.original_unit_cost
            or lot.unit_cost
            or Decimal("0")
        )
        delta_per_unit = new_unit_cost - old_cost
        delta_extended = delta_per_unit * lot.quantity_kg

        # Update lot
        if lot.original_unit_cost is None:
            lot.original_unit_cost = old_cost
        lot.current_unit_cost = new_unit_cost
        # Flush to ensure lot update is visible
        self.db.flush()

        # Create revaluation record
        reval = Revaluation(
            item_id=lot.product_id,
            lot_id=lot.id,
            old_unit_cost=old_cost,
            new_unit_cost=new_unit_cost,
            delta_extended_cost=delta_extended,
            reason=reason,
            revalued_by=revalued_by,
            revalued_at=datetime.utcnow(),
        )
        self.db.add(reval)
        self.db.flush()

        if propagate:
            # Find downstream assemblies that consumed this lot
            dependencies = (
                self.db.query(AssemblyCostDependency)
                .filter(AssemblyCostDependency.consumed_lot_id == lot_id)
                .all()
            )

            # Refresh lot to ensure we have the latest state
            self.db.refresh(lot)

            # Propagate revaluation
            for dep in dependencies:
                produced_lot = self.db.get(InventoryLot, dep.produced_lot_id)
                if produced_lot:
                    # Get all consumed issues for this assembly
                    consumed_issues = self._get_consumed_issues_for_produced_lot(
                        produced_lot.id
                    )

                    # Recalculate with new cost
                    new_parent_cost = Decimal("0")
                    for issue in consumed_issues:
                        if issue["lot_id"] == lot_id:
                            new_parent_cost += issue["qty"] * new_unit_cost
                        else:
                            new_parent_cost += issue["qty"] * issue["unit_cost"]

                    new_parent_unit_cost = (
                        new_parent_cost / produced_lot.quantity_kg
                        if produced_lot.quantity_kg > 0
                        else Decimal("0")
                    )

                    # Update produced lot
                    old_parent_cost = (
                        produced_lot.current_unit_cost
                        or produced_lot.unit_cost
                        or Decimal("0")
                    )
                    produced_lot.current_unit_cost = new_parent_unit_cost

                    # Create revaluation entry for parent
                    reval_parent = Revaluation(
                        item_id=produced_lot.product_id,
                        lot_id=produced_lot.id,
                        old_unit_cost=old_parent_cost,
                        new_unit_cost=new_parent_unit_cost,
                        delta_extended_cost=(new_parent_unit_cost - old_parent_cost)
                        * produced_lot.quantity_kg,
                        reason=f"Propagated from lot {lot.lot_code}: {reason}",
                        revalued_by=revalued_by,
                        revalued_at=datetime.utcnow(),
                        propagated_to_assemblies=True,
                    )
                    self.db.add(reval_parent)

            reval.propagated_to_assemblies = len(dependencies) > 0

        return reval

    def _get_consumed_issues_for_produced_lot(
        self, produced_lot_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all consumed issues for a produced lot (for revaluation recalculation).

        Args:
            produced_lot_id: Produced lot ID

        Returns:
            List of issue dictionaries with lot_id, qty, unit_cost (using current lot cost)
        """
        dependencies = (
            self.db.query(AssemblyCostDependency)
            .filter(AssemblyCostDependency.produced_lot_id == produced_lot_id)
            .all()
        )

        issues = []
        for dep in dependencies:
            consumed_txn = self.db.get(InventoryTxn, dep.consumed_txn_id)
            if consumed_txn:
                # Use current lot cost (which may have been revalued)
                consumed_lot = self.db.get(InventoryLot, consumed_txn.lot_id)
                current_cost = (
                    consumed_lot.current_unit_cost
                    if consumed_lot
                    else (consumed_txn.unit_cost or Decimal("0"))
                )

                issues.append(
                    {
                        "lot_id": consumed_txn.lot_id,
                        "qty": abs(
                            consumed_txn.quantity_kg
                        ),  # Abs because issues are negative
                        "unit_cost": current_cost,  # Use current lot cost, not transaction cost
                    }
                )

        return issues

    def print_cogs_tree(self, cogs_data: Dict[str, Any], indent: int = 0) -> str:
        """
        Pretty-print COGS breakdown tree.

        Args:
            cogs_data: COGS data structure from inspect_cogs()
            indent: Current indentation level

        Returns:
            Formatted string representation
        """
        lines = []
        prefix = "  " * indent

        breakdown = cogs_data.get("breakdown", cogs_data)

        flags = []
        if breakdown.get("has_estimate"):
            flags.append("⚠ ESTIMATE")
        if breakdown.get("cost_source") == CostSource.STANDARD.value:
            flags.append("📊 STANDARD")

        flag_str = " ".join(flags) if flags else ""

        lines.append(f"{prefix}{breakdown['sku']}: {breakdown['name']}")
        lines.append(f"{prefix}  Unit Cost: ${breakdown['unit_cost']:.2f} {flag_str}")

        if breakdown.get("has_estimate") and breakdown.get("estimate_reason"):
            lines.append(f"{prefix}  ⚠ Reason: {breakdown['estimate_reason']}")

        if breakdown.get("children"):
            for child in breakdown["children"]:
                lines.append(self.print_cogs_tree({"breakdown": child}, indent + 1))

        return "\n".join(lines)
