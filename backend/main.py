
import csv
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from backend.approval_api import router as approval_router
from database.db import get_ticket as get_db_ticket


# --------------------------------------------------
# 1. APPLICATION CONFIGURATION
# --------------------------------------------------

app = FastAPI(
    title="TelecomCare AI API",
    description="Backend API for Agentic IT Ticket Automation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(approval_router)


# --------------------------------------------------
# 2. CSV DATASET CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TICKET_FILE = PROJECT_ROOT / "data" / "tickets.csv"


def read_tickets():
    """Read synthetic tickets from CSV."""

    if not TICKET_FILE.exists():
        return []

    with open(TICKET_FILE, "r", encoding="utf-8") as file:
        return list(csv.DictReader(file))


# --------------------------------------------------
# 3. TICKET REQUEST MODEL
# --------------------------------------------------

class TicketRequest(BaseModel):

    employee_id: str = Field(min_length=3, max_length=30)

    description: str = Field(min_length=5, max_length=1000)

    category: str = "General"
    priority: str = "Medium"


# --------------------------------------------------
# 4. HEALTH CHECK
# --------------------------------------------------

@app.get("/health")
def health_check():

    return {
        "status": "healthy",
        "application": "TelecomCare AI",
        "message": "Backend is running successfully"
    }


# --------------------------------------------------
# 5. GET SYNTHETIC CSV TICKETS
# --------------------------------------------------

@app.get("/tickets")
def get_all_tickets():

    tickets = read_tickets()

    return {
        "total_tickets": len(tickets),
        "tickets": tickets
    }


# --------------------------------------------------
# 6. GET TICKET WITH EMPLOYEE OWNERSHIP CHECK
# --------------------------------------------------

@app.get("/tickets/{ticket_id}")
def get_ticket_by_id(
    ticket_id: str,
    employee_id: str = Query(
        ...,
        min_length=3,
        max_length=30
    )
):

    # Check SQLite database first
    ticket = get_db_ticket(ticket_id)

    if ticket:

        if ticket["employee_id"] != employee_id:
            raise HTTPException(
                status_code=403,
                detail="You are not authorized to view this ticket."
            )

        return ticket

    # Check existing synthetic CSV tickets
    tickets = read_tickets()

    for csv_ticket in tickets:

        if csv_ticket["ticket_id"] == ticket_id:

            if csv_ticket["employee_id"] != employee_id:
                raise HTTPException(
                    status_code=403,
                    detail="You are not authorized to view this ticket."
                )

            return csv_ticket

    raise HTTPException(
        status_code=404,
        detail="Ticket not found"
    )


# --------------------------------------------------
# 7. CREATE SYNTHETIC CSV TICKET
# --------------------------------------------------

@app.post("/tickets", status_code=201)
def create_csv_ticket(request: TicketRequest):

    tickets = read_tickets()

    ticket_id = f"TEL-{1001 + len(tickets)}"

    new_ticket = {
        "ticket_id": ticket_id,
        "employee_id": request.employee_id,
        "description": request.description,
        "category": request.category,
        "priority": request.priority,
        "status": "Open",
        "resolution": "Pending"
    }

    file_exists = TICKET_FILE.exists()

    with open(
        TICKET_FILE,
        "a",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=new_ticket.keys()
        )

        if not file_exists or TICKET_FILE.stat().st_size == 0:
            writer.writeheader()

        writer.writerow(new_ticket)

    return {
        "message": "Ticket created successfully",
        "ticket": new_ticket
    }


# --------------------------------------------------
# 8. ROOT API
# --------------------------------------------------

@app.get("/")
def root():

    return {
        "message": "Welcome to TelecomCare AI",
        "documentation": "/docs",
        "health": "/health"
    }


# --------------------------------------------------
# 9. APPLICATION STARTUP
# --------------------------------------------------

@app.on_event("startup")
def application_startup():

    print("[TELECOMCARE] Backend started successfully.")
    print("[TELECOMCARE] SQLite ticket tracking enabled.")
    print("[TELECOMCARE] Employee ownership validation enabled.")
    print("[TELECOMCARE] Manager and IT approval APIs enabled.")
