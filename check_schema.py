import sqlite3

conn = sqlite3.connect('db/vnd.db')
cursor = conn.cursor()

# Check if table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='excise_rates'")
exists = cursor.fetchone()
if not exists:
    print("excise_rates table does not exist!")
else:
    cursor.execute('PRAGMA table_info(excise_rates)')
    cols = cursor.fetchall()
    print('excise_rates columns:')
    if not cols:
        print("  No columns found")
    else:
        for c in cols:
            print(f"  {c[1]} ({c[2]}, nullable={not c[3]}, default={c[4]})")
conn.close()

