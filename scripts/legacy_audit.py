#!/usr/bin/env python3
"""Scan legacy source/data and emit mapping CSV + YAML specs."""

import argparse
import csv
import re
import sys
from pathlib import Path
from typing import Any, Dict

import yaml


class LegacyFileScanner:
    """Scans legacy files and extracts field mappings."""

    def __init__(self, src_dir: Path, data_dir: Path, out_dir: Path):
        self.src_dir = src_dir
        self.data_dir = data_dir
        self.out_dir = out_dir
        self.mappings = []
        self.file_specs = {}

    def scan_bas_files(self) -> None:
        """Scan .BAS files for field definitions and file operations."""
        for bas_file in self.src_dir.glob("**/*.BAS"):
            self._scan_bas_file(bas_file)

    def _scan_bas_file(self, bas_file: Path) -> None:
        """Scan a single .BAS file for field definitions."""
        print(f"Scanning {bas_file}")

        try:
            content = bas_file.read_text(encoding="cp437", errors="ignore")
        except UnicodeDecodeError:
            try:
                content = bas_file.read_text(encoding="utf-8", errors="ignore")
            except:
                content = bas_file.read_bytes().decode("latin-1", errors="ignore")

        # Extract TYPE definitions
        type_pattern = r"TYPE\s+(\w+)\s*\n(.*?)\nEND TYPE"
        type_matches = re.finditer(
            type_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE
        )

        for match in type_matches:
            type_name = match.group(1)
            type_body = match.group(2)
            self._parse_type_definition(bas_file, type_name, type_body)

        # Extract FIELD statements
        field_pattern = r"FIELD\s+#(\d+),\s*(\d+)\s+AS\s+(\w+)"
        field_matches = re.finditer(field_pattern, content, re.IGNORECASE)

        for match in field_matches:
            file_num = match.group(1)
            length = int(match.group(2))
            field_name = match.group(3)
            self._add_field_mapping(
                bas_file, field_name, 0, length, "STRING", "unknown", field_name
            )

        # Extract OPEN statements to identify data files
        open_pattern = r'OPEN\s+["\']([^"\']+)["\']\s+FOR\s+(\w+)\s+AS\s+#(\d+)'
        open_matches = re.finditer(open_pattern, content, re.IGNORECASE)

        for match in open_matches:
            filename = match.group(1)
            mode = match.group(2)
            file_num = match.group(3)
            self._identify_data_file(bas_file, filename, file_num)

    def _parse_type_definition(
        self, bas_file: Path, type_name: str, type_body: str
    ) -> None:
        """Parse a TYPE definition and extract field mappings."""
        lines = type_body.strip().split("\n")
        offset = 0

        for line in lines:
            line = line.strip()
            if not line or line.startswith("REM") or line.startswith("'"):
                continue

            # Parse field definitions like: field_name AS type
            field_match = re.match(r"(\w+)\s+AS\s+(\w+)", line, re.IGNORECASE)
            if field_match:
                field_name = field_match.group(1)
                field_type = field_match.group(2)

                # Determine length based on type
                length = self._get_type_length(field_type)
                field_type_str = self._map_basic_type(field_type)

                self._add_field_mapping(
                    bas_file,
                    f"{type_name}.{field_name}",
                    offset,
                    length,
                    field_type_str,
                    self._map_to_table(type_name),
                    field_name,
                )
                offset += length

    def _get_type_length(self, basic_type: str) -> int:
        """Get the length of a BASIC type."""
        type_lengths = {
            "INTEGER": 2,
            "LONG": 4,
            "SINGLE": 4,
            "DOUBLE": 8,
            "STRING": 255,  # Default string length
            "STRING*": 255,
        }

        # Handle STRING*n format
        if basic_type.upper().startswith("STRING*"):
            try:
                return int(basic_type.split("*")[1])
            except:
                return 255

        return type_lengths.get(basic_type.upper(), 4)

    def _map_basic_type(self, basic_type: str) -> str:
        """Map BASIC types to our field types."""
        type_mapping = {
            "INTEGER": "INTEGER",
            "LONG": "INTEGER",
            "SINGLE": "DECIMAL",
            "DOUBLE": "DECIMAL",
            "STRING": "STRING",
            "STRING*": "STRING",
        }

        if basic_type.upper().startswith("STRING*"):
            return "STRING"

        return type_mapping.get(basic_type.upper(), "STRING")

    def _map_to_table(self, type_name: str) -> str:
        """Map TYPE names to database tables."""
        table_mapping = {
            "PRODUCT": "products",
            "CUSTOMER": "customers",
            "SUPPLIER": "suppliers",
            "FORMULA": "formulas",
            "FORMULA_LINE": "formula_lines",
            "INVENTORY": "inventory_lots",
            "WORK_ORDER": "work_orders",
            "BATCH": "batches",
            "INVOICE": "invoices",
            "PRICE_LIST": "price_lists",
            "PACK_UNIT": "pack_units",
        }

        return table_mapping.get(type_name.upper(), "unknown")

    def _add_field_mapping(
        self,
        bas_file: Path,
        field_name: str,
        offset: int,
        length: int,
        field_type: str,
        table: str,
        column: str,
    ) -> None:
        """Add a field mapping to the list."""
        self.mappings.append(
            {
                "legacy_file": bas_file.name,
                "field": field_name,
                "offset": offset,
                "length": length,
                "type": field_type,
                "new_table": table,
                "new_column": column,
                "notes": f"Auto-detected from {bas_file.name}",
            }
        )

    def _identify_data_file(self, bas_file: Path, filename: str, file_num: str) -> None:
        """Identify data files referenced in OPEN statements."""
        data_file_path = self.data_dir / filename
        if data_file_path.exists():
            self._scan_data_file(data_file_path, bas_file, file_num)

    def _scan_data_file(self, data_file: Path, bas_file: Path, file_num: str) -> None:
        """Scan a data file and create a YAML spec."""
        print(f"Scanning data file {data_file}")

        spec = {
            "file_name": data_file.name,
            "file_path": str(data_file),
            "file_number": file_num,
            "source_bas": bas_file.name,
            "record_length": 0,
            "fields": [],
        }

        # Try to determine record structure by analyzing the file
        try:
            with data_file.open("rb") as f:
                # Read first few records to analyze structure
                sample_data = f.read(1024)

                # Look for patterns that might indicate record boundaries
                # This is a heuristic approach - in practice, you'd need more sophisticated analysis
                record_length = self._estimate_record_length(sample_data)
                spec["record_length"] = record_length

                # Create placeholder fields based on estimated record length
                if record_length > 0:
                    self._create_placeholder_fields(spec, record_length)

        except Exception as e:
            print(f"Error scanning {data_file}: {e}")
            spec["error"] = str(e)

        self.file_specs[data_file.name] = spec

    def _estimate_record_length(self, sample_data: bytes) -> int:
        """Estimate record length from sample data."""
        # Simple heuristic: look for repeated patterns
        if len(sample_data) < 100:
            return len(sample_data)

        # Look for common record lengths
        common_lengths = [32, 64, 128, 256, 512, 1024]

        for length in common_lengths:
            if len(sample_data) % length == 0:
                return length

        # Default to a reasonable length
        return 128

    def _create_placeholder_fields(
        self, spec: Dict[str, Any], record_length: int
    ) -> None:
        """Create placeholder field definitions."""
        # This is a simplified approach - in practice, you'd need more sophisticated analysis
        field_count = min(record_length // 8, 20)  # Assume max 20 fields

        for i in range(field_count):
            field_length = min(8, record_length // field_count)
            spec["fields"].append(
                {
                    "name": f"field_{i + 1}",
                    "offset": i * field_length,
                    "length": field_length,
                    "type": "STRING",
                    "description": f"Auto-detected field {i + 1}",
                }
            )

    def scan_data_files(self) -> None:
        """Scan data files for structure."""
        for data_file in self.data_dir.glob("**/*"):
            if data_file.is_file() and data_file.suffix.lower() not in [
                ".bas",
                ".bi",
                ".txt",
            ]:
                self._scan_data_file(data_file, Path("unknown.bas"), "unknown")

    def write_outputs(self) -> None:
        """Write the mapping CSV and YAML specs."""
        # Write mapping CSV
        mapping_csv = self.out_dir / "legacy_mapping.csv"
        with mapping_csv.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "legacy_file",
                    "field",
                    "offset",
                    "length",
                    "type",
                    "new_table",
                    "new_column",
                    "notes",
                ],
            )
            writer.writeheader()
            writer.writerows(self.mappings)

        print(f"Wrote {mapping_csv} with {len(self.mappings)} mappings")

        # Write YAML specs
        specs_dir = self.out_dir / "specs"
        specs_dir.mkdir(exist_ok=True)

        for filename, spec in self.file_specs.items():
            spec_file = specs_dir / f"{filename}.yaml"
            with spec_file.open("w", encoding="utf-8") as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)

        print(f"Wrote {len(self.file_specs)} YAML specs to {specs_dir}")


def main():
    ap = argparse.ArgumentParser(
        description="Scan legacy files and create mapping specs"
    )
    ap.add_argument(
        "--src", required=True, help="Source directory containing .BAS files"
    )
    ap.add_argument(
        "--data", required=True, help="Data directory containing legacy data files"
    )
    ap.add_argument(
        "--out", required=True, help="Output directory for mapping CSV and YAML specs"
    )

    args = ap.parse_args()

    src_dir = Path(args.src)
    data_dir = Path(args.data)
    out_dir = Path(args.out)

    if not src_dir.exists():
        print(f"Error: Source directory {src_dir} does not exist")
        sys.exit(1)

    if not data_dir.exists():
        print(f"Error: Data directory {data_dir} does not exist")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    scanner = LegacyFileScanner(src_dir, data_dir, out_dir)

    print("Scanning .BAS files...")
    scanner.scan_bas_files()

    print("Scanning data files...")
    scanner.scan_data_files()

    print("Writing outputs...")
    scanner.write_outputs()

    print("Legacy audit completed successfully!")


if __name__ == "__main__":
    main()
