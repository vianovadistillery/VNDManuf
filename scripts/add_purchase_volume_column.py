"""Script to add purchase_volume column to products table."""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import sqlite3

conn = sqlite3.connect('tpmanuf.db')
cursor = conn.cursor()

# Check if column exists
cursor.execute("PRAGMA table_info(products)")
cols = [row[1] for row in cursor.fetchall()]

if 'purchase_volume' not in cols:
    print("Adding purchase_volume column...")
    cursor.execute("ALTER TABLE products ADD COLUMN purchase_volume NUMERIC(12, 3)")
    conn.commit()
    print("Column added successfully!")
else:
    print("Column purchase_volume already exists.")

conn.close()

