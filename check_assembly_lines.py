import sqlite3

conn = sqlite3.connect("tpmanuf.db")
cursor = conn.cursor()

# Check if assembly_lines table exists
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='assembly_lines'"
)
assembly_lines_exists = cursor.fetchone()
print(f"assembly_lines table exists: {assembly_lines_exists is not None}")

if assembly_lines_exists:
    cursor.execute("PRAGMA table_info(assembly_lines)")
    columns = cursor.fetchall()
    print("\nassembly_lines table columns:")
    for col in columns:
        print(f"  {col}")
else:
    print("\nassembly_lines table does not exist")

conn.close()
