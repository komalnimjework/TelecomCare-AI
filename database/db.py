import sqlite3
from pathlib import Path
from datetime import datetime


# --------------------------------------------------
# 1. DATABASE CONFIGURATION
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATABASE_PATH = PROJECT_ROOT / "database" / "tickets.db"


# --------------------------------------------------
# 2. DATABASE CONNECTION
# --------------------------------------------------

def get_connection():

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# --------------------------------------------------
# 3. INITIALIZE DATABASE
# --------------------------------------------------

def initialize_db():

    connection = get_connection()

    cursor = connection.cursor()

    # Employee IT tickets
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id TEXT UNIQUE,

            employee_id TEXT NOT NULL,

            employee_name TEXT,

            manager_id TEXT NOT NULL,

            it_approver_id TEXT NOT NULL,

            category TEXT NOT NULL,

            priority TEXT NOT NULL,

            description TEXT NOT NULL,

            requested_action TEXT,

            business_justification TEXT,

            current_approver TEXT,

            status TEXT NOT NULL,

            created_at TEXT NOT NULL,

            updated_at TEXT NOT NULL

        )
    """)

    # Manager and IT approval history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS approvals (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id TEXT NOT NULL,

            approval_stage TEXT NOT NULL,

            approver_id TEXT NOT NULL,

            decision TEXT NOT NULL,

            comments TEXT,

            approved_at TEXT NOT NULL,

            FOREIGN KEY (ticket_id)
                REFERENCES tickets(ticket_id)

        )
    """)

    # Action execution history
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS action_history (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            ticket_id TEXT NOT NULL,

            action_name TEXT NOT NULL,

            execution_status TEXT NOT NULL,

            details TEXT,

            executed_at TEXT NOT NULL,

            FOREIGN KEY (ticket_id)
                REFERENCES tickets(ticket_id)

        )
    """)

    connection.commit()

    connection.close()

    print("[DATABASE] Database initialized successfully.")


# --------------------------------------------------
# 4. CREATE EMPLOYEE TICKET
# --------------------------------------------------

def create_ticket(
    employee_id,
    manager_id,
    it_approver_id,
    category,
    priority,
    description,
    employee_name="Employee",
    requested_action=None,
    business_justification=None
):

    connection = get_connection()

    cursor = connection.cursor()

    now = datetime.now().isoformat()

    try:

        # Determine initial ticket status
        if category in [
            "Software Installation",
            "Access Request"
        ]:

            status = "PENDING_MANAGER"
            current_approver = manager_id

        elif category == "Password":

            status = "SELF_SERVICE"
            current_approver = None

        else:

            status = "AUTO_RESOLVED"
            current_approver = None

        # Insert ticket first to generate unique database ID
        cursor.execute("""
            INSERT INTO tickets (
                employee_id,
                employee_name,
                manager_id,
                it_approver_id,
                category,
                priority,
                description,
                requested_action,
                business_justification,
                current_approver,
                status,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            employee_id,
            employee_name,
            manager_id,
            it_approver_id,
            category,
            priority,
            description,
            requested_action,
            business_justification,
            current_approver,
            status,
            now,
            now
        ))

        # Generate a unique ticket number
        database_id = cursor.lastrowid

        ticket_id = f"TC-{datetime.now().year}-{database_id:04d}"

        cursor.execute("""
            UPDATE tickets
            SET ticket_id = ?
            WHERE id = ?
        """, (ticket_id, database_id))

        connection.commit()

        print(f"[DATABASE] Ticket created: {ticket_id}")

        return {
            "success": True,
            "ticket_id": ticket_id,
            "status": status,
            "current_approver": current_approver
        }

    except Exception as error:

        connection.rollback()

        return {
            "success": False,
            "error": str(error)
        }

    finally:

        connection.close()


# --------------------------------------------------
# 5. GET TICKET DETAILS
# --------------------------------------------------

def get_ticket(ticket_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tickets
        WHERE ticket_id = ?
    """, (ticket_id,))

    ticket = cursor.fetchone()

    connection.close()

    return dict(ticket) if ticket else None


# --------------------------------------------------
# 6. GET EMPLOYEE TICKETS
# --------------------------------------------------

def get_employee_tickets(employee_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM tickets
        WHERE employee_id = ?
        ORDER BY id DESC
    """, (employee_id,))

    tickets = cursor.fetchall()

    connection.close()

    return [dict(ticket) for ticket in tickets]


# --------------------------------------------------
# 7. GET PENDING APPROVALS
# --------------------------------------------------

def get_pending_approvals(stage, approver_id=None):

    connection = get_connection()

    cursor = connection.cursor()

    if stage == "MANAGER":

        status = "PENDING_MANAGER"

    elif stage == "IT":

        status = "PENDING_IT"

    else:

        connection.close()
        return []

    if approver_id:

        column = (
            "manager_id"
            if stage == "MANAGER"
            else "it_approver_id"
        )

        cursor.execute(f"""
            SELECT *
            FROM tickets
            WHERE status = ?
            AND {column} = ?
            ORDER BY id ASC
        """, (status, approver_id))

    else:

        cursor.execute("""
            SELECT *
            FROM tickets
            WHERE status = ?
            ORDER BY id ASC
        """, (status,))

    tickets = cursor.fetchall()

    connection.close()

    return [dict(ticket) for ticket in tickets]


# --------------------------------------------------
# 8. UPDATE TICKET STATUS
# --------------------------------------------------

def update_ticket_status(
    ticket_id,
    status,
    current_approver=None
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        UPDATE tickets

        SET status = ?,
            current_approver = ?,
            updated_at = ?

        WHERE ticket_id = ?
    """, (
        status,
        current_approver,
        datetime.now().isoformat(),
        ticket_id
    ))

    connection.commit()

    updated = cursor.rowcount > 0

    connection.close()

    return updated


# --------------------------------------------------
# 9. RECORD APPROVAL HISTORY
# --------------------------------------------------

def record_approval(
    ticket_id,
    approval_stage,
    approver_id,
    decision,
    comments=""
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO approvals (
            ticket_id,
            approval_stage,
            approver_id,
            decision,
            comments,
            approved_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        ticket_id,
        approval_stage,
        approver_id,
        decision,
        comments,
        datetime.now().isoformat()
    ))

    connection.commit()

    connection.close()

    return True


# --------------------------------------------------
# 10. GET APPROVAL HISTORY
# --------------------------------------------------

def get_approval_history(ticket_id):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM approvals
        WHERE ticket_id = ?
        ORDER BY id ASC
    """, (ticket_id,))

    records = cursor.fetchall()

    connection.close()

    return [dict(record) for record in records]


# --------------------------------------------------
# 11. RECORD ACTION EXECUTION
# --------------------------------------------------

def record_action(
    ticket_id,
    action_name,
    execution_status,
    details=""
):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO action_history (
            ticket_id,
            action_name,
            execution_status,
            details,
            executed_at
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        ticket_id,
        action_name,
        execution_status,
        details,
        datetime.now().isoformat()
    ))

    connection.commit()

    connection.close()

    return True


# --------------------------------------------------
# 12. INITIALIZE WHEN RUN DIRECTLY
# --------------------------------------------------

if __name__ == "__main__":

    initialize_db()