"""Clean up temporary Alembic tables from failed migrations."""

import sqlite3

conn = sqlite3.connect("tpmanuf.db")
cursor = conn.cursor()

# Find all temporary tables
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '_alembic_tmp%'"
)
tables = cursor.fetchall()

for table in tables:
    table_name = table[0]
    print(f"Dropping table: {table_name}")
    cursor.execute(f"DROP TABLE IF EXISTS {table_name}")

conn.commit()
conn.close()
print(f"Cleaned up {len(tables)} temporary tables")
