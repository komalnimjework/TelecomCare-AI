from database.db import get_ticket

ticket = get_ticket("TC-2026-0010")

print("\n--- ACCESS REQUEST DETAILS ---")

if ticket:
    print("Ticket ID:", ticket["ticket_id"])
    print("Category:", ticket["category"])
    print("Requested Action:", ticket["requested_action"])
    print("Status:", ticket["status"])
    print("Description:", ticket["description"])
else:
    print("Ticket not found.")