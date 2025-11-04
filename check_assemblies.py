import sqlite3

conn = sqlite3.connect("tpmanuf.db")
cursor = conn.cursor()

# Check alembic version
cursor.execute("SELECT version_num FROM alembic_version")
versions = cursor.fetchall()
print(f"Current alembic versions: {versions}")

# Check assemblies table structure
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='assemblies'"
)
if cursor.fetchone():
    cursor.execute("PRAGMA table_info(assemblies)")
    columns = cursor.fetchall()
    print("\nassemblies table columns:")
    for col in columns:
        print(f"  {col}")
else:
    print("\nassemblies table does not exist")

conn.close()
