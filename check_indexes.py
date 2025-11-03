import sqlite3

conn = sqlite3.connect('tpmanuf.db')
cursor = conn.cursor()

# Check all indexes on assemblies table
cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='assemblies'")
indexes = cursor.fetchall()
print("\nIndexes on assemblies table:")
for idx in indexes:
    print(f"  {idx}")

conn.close()

