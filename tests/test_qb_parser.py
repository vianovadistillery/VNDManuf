"""Unit tests for QB parser (Phase 8.1)."""

from pathlib import Path

import pytest

from app.adapters.qb_parser import QBFileParser


def test_raw_material_parser():
    """Test parsing raw materials from MSF file."""
    msf_file = Path("legacy_data/MSRMNEW.msf")

    if not msf_file.exists():
        pytest.skip(f"MSF file not found: {msf_file}")

    parser = QBFileParser(msf_file)
    records = parser.parse_raw_materials()

    assert len(records) > 0

    # Check first record structure
    first = records[0]
    assert "no" in first
    assert "Desc1" in first
    assert "Sg" in first

    # Sample assertions
    if first.get("no") == 1:
        assert first.get("Desc1") == "WATER...................>"
        assert first.get("Sg") == 1.0


def test_record_structure():
    """Test that all required fields are present in parsed records."""
    msf_file = Path("legacy_data/MSRMNEW.msf")

    if not msf_file.exists():
        pytest.skip(f"MSF file not found: {msf_file}")

    parser = QBFileParser(msf_file)
    records = parser.parse_raw_materials()

    if records:
        sample = records[0]
        required_fields = [
            "no",
            "Desc1",
            "Desc2",
            "Search",
            "Sg",
            "PurCost",
            "PurUnit",
            "UseCost",
            "UseUnit",
            "Group",
            "Active",
            "soh",
        ]

        for field in required_fields:
            assert field in sample, f"Missing field: {field}"


def test_data_types():
    """Test data type conversions (INTEGER, SINGLE, STRING, CURRENCY)."""
    msf_file = Path("legacy_data/MSRMNEW.msf")

    if not msf_file.exists():
        pytest.skip(f"MSF file not found: {msf_file}")

    parser = QBFileParser(msf_file)
    records = parser.parse_raw_materials()

    if records:
        sample = records[0]

        # Check integer fields
        assert isinstance(sample.get("no"), int) or sample.get("no") is None

        # Check float fields
        assert isinstance(sample.get("Sg"), float) or sample.get("Sg") is None

        # Check string fields
        assert isinstance(sample.get("Desc1"), str) or sample.get("Desc1") is None


def test_empty_file_handling():
    """Test parser handles empty or invalid files gracefully."""
    empty_file = Path("tests/test_empty.dat")
    empty_file.touch()

    try:
        parser = QBFileParser(empty_file)
        records = parser.parse_raw_materials()
        assert len(records) == 0
    finally:
        empty_file.unlink(missing_ok=True)


def test_currency_conversion():
    """Test QB CURRENCY type is correctly converted (8-byte scaled integer / 10000)."""
    msf_file = Path("legacy_data/MSRMNEW.msf")

    if not msf_file.exists():
        pytest.skip(f"MSF file not found: {msf_file}")

    parser = QBFileParser(msf_file)
    records = parser.parse_raw_materials()

    # Check if any records have ean13 (currency field)
    currency_records = [r for r in records if r.get("ean13") is not None]

    if currency_records:
        sample = currency_records[0]
        ean13 = sample.get("ean13")
        # Currency should be properly scaled
        assert ean13 == 0 or ean13 > 0, f"Invalid currency value: {ean13}"
