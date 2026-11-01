import sqlite3

connection = sqlite3.connect("database/tickets.db")
connection.row_factory = sqlite3.Row

rows = connection.execute(
    "SELECT * FROM action_history WHERE ticket_id = ?",
    ("TC-2026-0010",)
).fetchall()

print("\n--- ACCESS ACTION HISTORY ---")

for row in rows:
    print(dict(row))

connection.close()