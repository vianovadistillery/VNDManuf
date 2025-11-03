"""Quick script to check units table schema."""

import sqlite3

conn = sqlite3.connect("db/vnd.db")
c = conn.cursor()

# Check if units table exists
c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='units'")
if c.fetchone():
    print("Units table exists")
    # Get schema
    c.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='units'")
    row = c.fetchone()
    if row:
        print("\nSchema:")
        print(row[0])

    # Get columns
    c.execute("PRAGMA table_info(units)")
    cols = c.fetchall()
    print("\nColumns:")
    for col in cols:
        print(f"  {col[1]} ({col[2]})")
else:
    print("Units table does NOT exist in database")

conn.close()
