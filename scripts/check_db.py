#!/usr/bin/env python3
"""Check database schema"""

import sqlite3

conn = sqlite3.connect("tpmanuf.db")
cur = conn.cursor()
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cur.fetchall()]
print("Tables in database:", tables)

# Check for raw materials table
if "raw_materials" in tables:
    cur.execute("SELECT COUNT(*) FROM raw_materials")
    count = cur.fetchone()[0]
    print(f"Raw Materials count: {count}")

    if count > 0:
        cur.execute("SELECT * FROM raw_materials LIMIT 3")
        for row in cur.fetchall():
            print(row)

conn.close()
