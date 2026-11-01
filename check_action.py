import sqlite3

connection = sqlite3.connect("database/tickets.db")
connection.row_factory = sqlite3.Row

query = """
SELECT *
FROM action_history
WHERE ticket_id = ?
"""

rows = connection.execute(query, ("TC-2026-0009",)).fetchall()

print("\n--- IT ACTION HISTORY ---")

if rows:
    for row in rows:
        print(dict(row))
else:
    print("No action history found.")

connection.close()