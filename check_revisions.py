import sqlite3

conn = sqlite3.connect('tpmanuf.db')
cursor = conn.cursor()

# Check alembic versions
cursor.execute('SELECT version_num FROM alembic_version')
versions = cursor.fetchall()
print("Applied alembic revisions:")
for v in versions:
    print(f"  {v[0]}")

conn.close()

