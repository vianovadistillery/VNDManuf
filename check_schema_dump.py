import sqlite3
import json

conn = sqlite3.connect('tpmanuf.db')
cursor = conn.cursor()

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cursor.fetchall()]

schema_info = {}
for table in tables:
    if table == 'sqlite_sequence' or table.startswith('alembic'):
        continue
    
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    
    schema_info[table] = {
        'columns': [{'name': col[1], 'type': col[2], 'notnull': col[3], 'default': col[4], 'pk': col[5]} for col in columns]
    }
    
    # Get indexes
    cursor.execute(f"PRAGMA index_list({table})")
    indexes = cursor.fetchall()
    schema_info[table]['indexes'] = [idx[1] for idx in indexes if idx[1]]

print(json.dumps(schema_info, indent=2))

conn.close()

