import sqlite3

conn = sqlite3.connect("db/vnd.db")
cursor = conn.cursor()

# Check alembic version
cursor.execute("SELECT version_num FROM alembic_version;")
version = cursor.fetchone()
print(f"Current alembic version: {version}")

# Check if excise_rates table exists
cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table' AND name='excise_rates';"
)
table_exists = cursor.fetchone()
print(f"excise_rates table exists: {table_exists is not None}")

if table_exists:
    cursor.execute("PRAGMA table_info(excise_rates);")
    result = cursor.fetchall()
    print("excise_rates table structure:")
    for row in result:
        print(row)

conn.close()
