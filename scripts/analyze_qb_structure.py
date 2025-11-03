#!/usr/bin/env python3
"""
Analyze QuickBASIC TPManuf source code structure.
Catalog modules, extract TYPE definitions, map dependencies.
"""

import csv
import re
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Set

# Project root
ROOT = Path(__file__).parent.parent
SRC_DIR = ROOT / "legacy_data/Src"


def extract_type_definitions(filepath: Path) -> List[dict]:
    """Extract TYPE...END TYPE definitions from a file."""
    types = []
    with open(filepath, "r", encoding="cp437", errors="ignore") as f:
        content = f.read()

    # Find TYPE definitions
    pattern = r"TYPE\s+(\w+)\s+(.*?)END TYPE"
    matches = re.finditer(pattern, content, re.DOTALL | re.IGNORECASE)

    for match in matches:
        type_name = match.group(1)
        fields_text = match.group(2)

        # Extract field definitions
        field_pattern = r"(\w+(?:\([^)]+\))?)\s+AS\s+([^\n]+)"
        fields = re.findall(field_pattern, fields_text)

        type_info = {"name": type_name, "source_file": filepath.name, "fields": []}

        for field_def in fields:
            field_name = field_def[0].strip()
            field_type = field_def[1].strip()
            type_info["fields"].append({"name": field_name, "type": field_type})

        types.append(type_info)

    return types


def extract_includes(filepath: Path) -> Set[str]:
    """Extract $INCLUDE statements."""
    includes = set()
    with open(filepath, "r", encoding="cp437", errors="ignore") as f:
        for line in f:
            # QuickBASIC include format: '$INCLUDE: 'file.inc''
            match = re.search(
                r"\$INCLUDE[:\s]+['\"]([\w./]+)['\"]", line, re.IGNORECASE
            )
            if match:
                includes.add(match.group(1))
    return includes


def catalog_menu_structure(menufile: Path) -> Dict:
    """Extract menu options from MENU/MAIN menu files."""
    menu_structure = {
        "options": [],
        "chains": [],  # Programs to chain to
    }

    with open(menufile, "r", encoding="cp437", errors="ignore") as f:
        content = f.read()

        # Find menu options (LOCATE followed by PRINT)
        option_pattern = r'LOCATE\s+\d+,\s+\d+:\s+PRINT\s+"([^"]+)"'
        options = re.findall(option_pattern, content)
        menu_structure["options"] = options

        # Find chain statements
        chain_pattern = r"CHAIN\s+(\w+)"
        chains = re.findall(chain_pattern, content, re.IGNORECASE)
        menu_structure["chains"] = chains

    return menu_structure


def main():
    print("Analyzing QuickBASIC TPManuf source structure...")
    print(f"Source directory: {SRC_DIR}")

    # File type statistics
    bas_files = list(SRC_DIR.glob("*.BAS"))
    inc_files = list(SRC_DIR.glob("*.inc"))
    bix_files = list(SRC_DIR.glob("*.BIX"))

    print(f"\nFound {len(bas_files)} .BAS files")
    print(f"Found {len(inc_files)} .INC files")
    print(f"Found {len(bix_files)} .BIX files")

    # Analyze main menu
    main_menu_files = [
        SRC_DIR / "MENUTP.BAS",
        SRC_DIR / "MSMENU.BAS",
        SRC_DIR / "CSMENU.BAS",
        SRC_DIR / "DSMENU.BAS",
        SRC_DIR / "FIMENU.BAS",
        SRC_DIR / "QSMENU.BAS",
    ]

    menus = {}
    for menu_file in main_menu_files:
        if menu_file.exists():
            menus[menu_file.name] = catalog_menu_structure(menu_file)

    # Extract TYPE definitions
    all_types = []
    for inc_file in inc_files:
        types = extract_type_definitions(inc_file)
        all_types.extend(types)

    # Analyze includes
    include_map = defaultdict(set)
    for bas_file in bas_files:
        includes = extract_includes(bas_file)
        include_map[bas_file.name] = includes

    # Output results
    output_dir = ROOT / "docs/legacy"
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Module inventory
    with open(output_dir / "qb_module_inventory.md", "w") as f:
        f.write("# QuickBASIC TPManuf Module Inventory\n\n")
        f.write(f"Total .BAS files: {len(bas_files)}\n")
        f.write(f"Total .INC files: {len(inc_files)}\n")
        f.write(f"Total .BIX files: {len(bix_files)}\n\n")

        f.write("## Main Menu Programs\n\n")
        for menu_name, structure in menus.items():
            f.write(f"### {menu_name}\n\n")
            f.write("Options:\n")
            for opt in structure["options"]:
                f.write(f"- {opt}\n")
            f.write(f"\nChains to: {', '.join(structure['chains'])}\n\n")

    # 2. TYPE definitions
    with open(output_dir / "qb_type_definitions.md", "w") as f:
        f.write("# QuickBASIC TYPE Definitions\n\n")
        for type_info in all_types:
            f.write(f"## {type_info['name']}\n")
            f.write(f"Source: {type_info['source_file']}\n")
            f.write(f"Fields: {len(type_info['fields'])}\n\n")
            for field in type_info["fields"]:
                f.write(f"- {field['name']}: {field['type']}\n")
            f.write("\n")

    # 3. CSV data dictionary
    with open(output_dir / "qb_data_dictionary.csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(
            csvfile, fieldnames=["type", "field", "qbasic_type", "source_file"]
        )
        writer.writeheader()

        for type_info in all_types:
            for field in type_info["fields"]:
                writer.writerow(
                    {
                        "type": type_info["name"],
                        "field": field["name"],
                        "qbasic_type": field["type"],
                        "source_file": type_info["source_file"],
                    }
                )

    # 4. Include dependencies
    with open(output_dir / "qb_include_map.md", "w") as f:
        f.write("# QuickBASIC Include Map\n\n")
        for bas_file, includes in sorted(include_map.items()):
            if includes:
                f.write(f"## {bas_file}\n")
                for inc in includes:
                    f.write(f"- {inc}\n")
                f.write("\n")

    print("\nAnalysis complete!")
    print(f"Results written to {output_dir}")
    print("- qb_module_inventory.md")
    print("- qb_type_definitions.md")
    print("- qb_data_dictionary.csv")
    print("- qb_include_map.md")


if __name__ == "__main__":
    main()
