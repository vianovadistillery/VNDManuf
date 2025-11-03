# tests/test_domain_rules.py
"""Tests for domain rules including units conversions and FIFO logic."""

from decimal import Decimal

import pytest

from app.adapters.db.models import InventoryLot
from app.domain.rules import (
    calculate_abv_mass,
    calculate_line_totals,
    fifo_issue,
    round_money,
    round_quantity,
    to_kg,
    to_liters,
    validate_non_negative_lot,
)


class TestUnitsConversions:
    """Test units conversion functions."""

    def test_to_kg_from_kg(self):
        """Test conversion from kg to kg (no change)."""
        result = to_kg(Decimal("100.0"), "kg")
        assert result.quantity_kg == Decimal("100.0")
        assert result.conversion_factor == Decimal("1")
        assert result.source_unit == "kg"

    def test_to_kg_from_liters(self):
        """Test conversion from liters to kg using density."""
        density = Decimal("0.8")  # 0.8 kg/L
        result = to_kg(Decimal("100.0"), "L", density)
        assert result.quantity_kg == Decimal("80.0")
        assert result.conversion_factor == density
        assert result.source_unit == "L"

    def test_to_kg_from_liters_no_density(self):
        """Test that missing density raises ValueError."""
        with pytest.raises(ValueError, match="Density required for liquid conversion"):
            to_kg(Decimal("100.0"), "L")

    def test_to_kg_unsupported_unit(self):
        """Test that unsupported units raise ValueError."""
        with pytest.raises(ValueError, match="Unsupported unit conversion"):
            to_kg(Decimal("100.0"), "gallons")

    def test_to_liters(self):
        """Test conversion from kg to liters."""
        quantity_kg = Decimal("80.0")
        density = Decimal("0.8")
        result = to_liters(quantity_kg, density)
        assert result == Decimal("100.0")

    def test_to_liters_zero_density(self):
        """Test that zero density raises ValueError."""
        with pytest.raises(ValueError, match="Density cannot be zero"):
            to_liters(Decimal("100.0"), Decimal("0"))


class TestRounding:
    """Test rounding functions."""

    def test_round_quantity_default(self):
        """Test quantity rounding to 3 decimal places."""
        assert round_quantity(Decimal("1.23456")) == Decimal("1.235")
        assert round_quantity(Decimal("1.23454")) == Decimal(
            "1.235"
        )  # Bankers' rounding
        assert round_quantity(Decimal("1.23450")) == Decimal(
            "1.234"
        )  # Bankers' rounding

    def test_round_quantity_custom_places(self):
        """Test quantity rounding to custom decimal places."""
        assert round_quantity(Decimal("1.23456"), 2) == Decimal("1.23")
        assert round_quantity(Decimal("1.23556"), 2) == Decimal("1.24")

    def test_round_money_default(self):
        """Test money rounding to 2 decimal places."""
        assert round_money(Decimal("1.23456")) == Decimal("1.23")
        assert round_money(Decimal("1.23556")) == Decimal("1.24")
        assert round_money(Decimal("1.23550")) == Decimal("1.24")  # Bankers' rounding


class TestFifoIssue:
    """Test FIFO issue logic."""

    def create_test_lot(
        self, lot_id: str, quantity: Decimal, unit_cost: Decimal = None
    ):
        """Create a test inventory lot."""
        lot = InventoryLot()
        lot.id = lot_id
        lot.quantity_kg = quantity
        lot.unit_cost = unit_cost or Decimal("0")
        lot.lot_code = f"LOT-{lot_id}"
        return lot

    def test_fifo_issue_sufficient_stock(self):
        """Test FIFO issue with sufficient stock."""
        lots = [
            self.create_test_lot("1", Decimal("50.0"), Decimal("10.0")),
            self.create_test_lot("2", Decimal("30.0"), Decimal("12.0")),
            self.create_test_lot("3", Decimal("20.0"), Decimal("15.0")),
        ]

        issues = fifo_issue(lots, Decimal("80.0"))

        assert len(issues) == 2
        assert issues[0].lot_id == "1"
        assert issues[0].quantity_kg == Decimal("50.0")
        assert issues[0].unit_cost == Decimal("10.0")
        assert issues[0].remaining_quantity_kg == Decimal("0.0")

        assert issues[1].lot_id == "2"
        assert issues[1].quantity_kg == Decimal("30.0")
        assert issues[1].unit_cost == Decimal("12.0")
        assert issues[1].remaining_quantity_kg == Decimal("0.0")

    def test_fifo_issue_partial_lot(self):
        """Test FIFO issue that partially consumes a lot."""
        lots = [
            self.create_test_lot("1", Decimal("50.0"), Decimal("10.0")),
            self.create_test_lot("2", Decimal("30.0"), Decimal("12.0")),
        ]

        issues = fifo_issue(lots, Decimal("60.0"))

        assert len(issues) == 2
        assert issues[0].quantity_kg == Decimal("50.0")
        assert issues[0].remaining_quantity_kg == Decimal("0.0")

        assert issues[1].quantity_kg == Decimal("10.0")
        assert issues[1].remaining_quantity_kg == Decimal("20.0")

    def test_fifo_issue_insufficient_stock(self):
        """Test FIFO issue with insufficient stock raises ValueError."""
        lots = [
            self.create_test_lot("1", Decimal("50.0")),
            self.create_test_lot("2", Decimal("30.0")),
        ]

        with pytest.raises(ValueError, match="Insufficient stock"):
            fifo_issue(lots, Decimal("100.0"))

    def test_fifo_issue_override_negative(self):
        """Test FIFO issue with override allows negative quantities."""
        lots = [
            self.create_test_lot("1", Decimal("50.0")),
            self.create_test_lot("2", Decimal("-10.0")),  # Negative lot
        ]

        issues = fifo_issue(lots, Decimal("60.0"), override_negative=True)

        assert len(issues) == 2
        assert issues[0].quantity_kg == Decimal("50.0")
        assert issues[1].quantity_kg == Decimal("10.0")

    def test_fifo_issue_zero_quantity(self):
        """Test FIFO issue with zero quantity returns empty list."""
        lots = [self.create_test_lot("1", Decimal("50.0"))]

        issues = fifo_issue(lots, Decimal("0.0"))
        assert len(issues) == 0

    def test_fifo_issue_negative_quantity(self):
        """Test FIFO issue with negative quantity returns empty list."""
        lots = [self.create_test_lot("1", Decimal("50.0"))]

        issues = fifo_issue(lots, Decimal("-10.0"))
        assert len(issues) == 0


class TestAbvCalculations:
    """Test ABV mass calculations."""

    def test_calculate_abv_mass(self):
        """Test ABV mass calculation."""
        volume_l = Decimal("100.0")
        abv_percent = Decimal("40.0")  # 40% ABV
        density = Decimal("0.95")  # 0.95 kg/L

        alcohol_mass = calculate_abv_mass(volume_l, abv_percent, density)

        # Expected: 100L * 0.4 * 0.789 kg/L = 31.56 kg
        expected = Decimal("31.56")
        assert alcohol_mass == expected


class TestLineTotals:
    """Test line total calculations."""

    def test_calculate_line_totals(self):
        """Test line total calculation."""
        quantity_kg = Decimal("10.0")
        unit_price_ex_tax = Decimal("5.00")
        tax_rate = Decimal("10.0")  # 10%

        ex_tax, tax_amount, inc_tax = calculate_line_totals(
            quantity_kg, unit_price_ex_tax, tax_rate
        )

        assert ex_tax == Decimal("50.00")
        assert tax_amount == Decimal("5.00")
        assert inc_tax == Decimal("55.00")

    def test_calculate_line_totals_zero_tax(self):
        """Test line total calculation with zero tax."""
        quantity_kg = Decimal("10.0")
        unit_price_ex_tax = Decimal("5.00")
        tax_rate = Decimal("0.0")

        ex_tax, tax_amount, inc_tax = calculate_line_totals(
            quantity_kg, unit_price_ex_tax, tax_rate
        )

        assert ex_tax == Decimal("50.00")
        assert tax_amount == Decimal("0.00")
        assert inc_tax == Decimal("50.00")


class TestLotValidation:
    """Test lot validation functions."""

    def test_validate_non_negative_lot_positive(self):
        """Test validation of positive lot quantity."""
        lot = InventoryLot()
        lot.quantity_kg = Decimal("100.0")
        lot.lot_code = "LOT-001"

        # Should not raise
        validate_non_negative_lot(lot)

    def test_validate_non_negative_lot_negative_no_override(self):
        """Test validation of negative lot quantity without override."""
        lot = InventoryLot()
        lot.quantity_kg = Decimal("-10.0")
        lot.lot_code = "LOT-001"

        with pytest.raises(ValueError, match="cannot have negative quantity"):
            validate_non_negative_lot(lot)

    def test_validate_non_negative_lot_negative_with_override(self):
        """Test validation of negative lot quantity with override."""
        lot = InventoryLot()
        lot.quantity_kg = Decimal("-10.0")
        lot.lot_code = "LOT-001"

        # Should not raise with override
        validate_non_negative_lot(lot, override=True, audit_note="Admin override")

    def test_validate_non_negative_lot_override_no_audit_note(self):
        """Test that override without audit note raises error."""
        lot = InventoryLot()
        lot.quantity_kg = Decimal("-10.0")
        lot.lot_code = "LOT-001"

        with pytest.raises(ValueError, match="Audit note required"):
            validate_non_negative_lot(lot, override=True)
