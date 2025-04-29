import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute("SELECT * FROM allocations")
rows = cursor.fetchall()

print("Allocations in the database:")
for row in rows:
    print(row)

conn.close()
