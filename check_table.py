import sqlite3

conn = sqlite3.connect('db/vnd.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(excise_rates);')
result = cursor.fetchall()
print("excise_rates table structure:")
for row in result:
    print(row)
conn.close()




