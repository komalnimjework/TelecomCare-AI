
import csv
import json
import random
from pathlib import Path

# Fixed seed makes the dataset reproducible.
random.seed(42)

DATA_DIR = Path(__file__).parent

# Synthetic IT ticket examples.
ticket_templates = [
    {
        "category": "VPN",
        "descriptions": [
            "Unable to connect to company VPN",
            "VPN disconnects frequently",
            "VPN authentication failed",
            "Cannot access internal network through VPN"
        ],
        "priority": "High"
    },
    {
        "category": "Network",
        "descriptions": [
            "Office internet connection is down",
            "Network is very slow",
            "Cannot connect to internal server",
            "Frequent network disconnections"
        ],
        "priority": "High"
    },
    {
        "category": "Software Installation",
        "descriptions": [
            "Need installation of Python software",
            "Unable to install approved application",
            "Software installation permission denied",
            "Need IDE installation for development"
        ],
        "priority": "Medium"
    },
    {
        "category": "Access Request",
        "descriptions": [
            "Unable to access company email",
            "Need access to internal application",
            "Account is locked",
            "Permission denied for shared folder"
        ],
        "priority": "Medium"
    },
    {
        "category": "Password Reset",
        "descriptions": [
            "Forgot company account password",
            "Unable to log in due to incorrect password",
            "Need password reset",
            "Account password has expired"
        ],
        "priority": "Medium"
    }
]

statuses = ["Open", "In Progress", "Resolved", "Escalated"]

tickets = []

for i in range(1, 201):
    template = random.choice(ticket_templates)

    ticket = {
        "ticket_id": f"TEL-{1000 + i}",
        "employee_id": f"EMP-{random.randint(100, 999)}",
        "description": random.choice(template["descriptions"]),
        "category": template["category"],
        "priority": template["priority"],
        "status": random.choice(statuses),
        "resolution": "Pending"
    }

    tickets.append(ticket)

# Save CSV file.
csv_path = DATA_DIR / "tickets.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=tickets[0].keys())
    writer.writeheader()
    writer.writerows(tickets)


# Synthetic troubleshooting knowledge base.
knowledge_base = [
    {
        "id": "KB001",
        "category": "VPN",
        "title": "VPN Connection Troubleshooting",
        "content": "If VPN connection fails, verify internet connectivity, check VPN client configuration, confirm the account is active, and retry authentication. If the issue continues, escalate to the network support team."
    },
    {
        "id": "KB002",
        "category": "Network",
        "title": "Network Connectivity Troubleshooting",
        "content": "Check physical network connections, verify Wi-Fi connectivity, restart the network adapter if permitted, and check whether internal services are reachable. Escalate persistent outages to network operations."
    },
    {
        "id": "KB003",
        "category": "Software Installation",
        "title": "Software Installation Process",
        "content": "Verify that the requested software is approved by IT. Check device compatibility and available disk space. Installation requiring administrator privileges must be approved by IT support."
    },
    {
        "id": "KB004",
        "category": "Access Request",
        "title": "Application Access Troubleshooting",
        "content": "Verify employee identity, confirm the application and required role, and check existing permissions. New access grants require manager approval and identity team authorization."
    },
    {
        "id": "KB005",
        "category": "Password Reset",
        "title": "Password Reset Procedure",
        "content": "Verify the employee through the approved identity verification process. Use the official password reset workflow. Never disclose passwords or request passwords in chat. Escalate identity verification failures."
    }
]

json_path = DATA_DIR / "knowledge_base.json"

with open(json_path, "w", encoding="utf-8") as file:
    json.dump(knowledge_base, file, indent=4)

print("Synthetic data generated successfully!")
print(f"Tickets created: {len(tickets)}")
print(f"Knowledge articles created: {len(knowledge_base)}")
print(f"CSV saved: {csv_path}")
print(f"Knowledge base saved: {json_path}")
