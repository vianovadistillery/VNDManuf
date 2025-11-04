import json

with open("docs/snapshot/db_schema.json") as f:
    data = json.load(f)

tables = [
    "assembly_lines",
    "assembly_cost_dependencies",
    "quality_test_definitions",
    "revaluations",
    "product_migration_map",
]

for t in tables:
    if t in data["tables"]:
        print(f"\n{'=' * 60}\n{t}\n{'=' * 60}")
        cols = data["tables"][t]["columns"]
        for col in cols:
            print(
                f"  {col['name']}: {col['type']} (nullable={not col['notnull']}, pk={col['primary_key']})"
            )
