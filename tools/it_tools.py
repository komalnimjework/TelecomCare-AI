
import hashlib
import hmac
import secrets
import sqlite3
import string
from datetime import datetime, timezone
from pathlib import Path


# ==================================================
# CONFIGURATION
# ==================================================

PASSWORD_DB = (
    Path(__file__).resolve().parent.parent
    / "database"
    / "tickets.db"
)

PBKDF2_ITERATIONS = 600_000


# ==================================================
# DATABASE CONNECTION
# ==================================================

def get_password_connection():

    PASSWORD_DB.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(PASSWORD_DB)
    connection.row_factory = sqlite3.Row

    connection.execute("""
        CREATE TABLE IF NOT EXISTS employee_credentials (
            employee_id TEXT PRIMARY KEY,
            salt BLOB NOT NULL,
            password_hash BLOB NOT NULL,
            must_change_password INTEGER DEFAULT 0,
            updated_at TEXT
        )
    """)

    connection.commit()

    return connection


# ==================================================
# PASSWORD VALIDATION
# ==================================================

def validate_password(password):

    if len(password) < 12:
        return False, "Password must contain at least 12 characters."

    if not any(c.isupper() for c in password):
        return False, "Password must contain an uppercase letter."

    if not any(c.islower() for c in password):
        return False, "Password must contain a lowercase letter."

    if not any(c.isdigit() for c in password):
        return False, "Password must contain a number."

    if not any(c in string.punctuation for c in password):
        return False, "Password must contain a special character."

    return True, "Password meets all security requirements."


# ==================================================
# PASSWORD HASHING
# ==================================================

def hash_password(password, salt):

    return hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PBKDF2_ITERATIONS
    )


# ==================================================
# CREATE OR RESET PASSWORD
# ==================================================

def set_password(employee_id, new_password):

    if not employee_id or len(employee_id.strip()) < 3:
        return {
            "success": False,
            "message": "Please enter a valid Employee ID."
        }

    valid, message = validate_password(new_password)

    if not valid:
        return {
            "success": False,
            "message": message
        }

    salt = secrets.token_bytes(16)

    password_hash = hash_password(
        new_password,
        salt
    )

    connection = get_password_connection()

    try:

        connection.execute(
            """
            INSERT INTO employee_credentials (
                employee_id,
                salt,
                password_hash,
                must_change_password,
                updated_at
            )
            VALUES (?, ?, ?, 0, ?)

            ON CONFLICT(employee_id) DO UPDATE SET
                salt = excluded.salt,
                password_hash = excluded.password_hash,
                must_change_password = 0,
                updated_at = excluded.updated_at
            """,
            (
                employee_id.strip(),
                salt,
                password_hash,
                datetime.now(timezone.utc).isoformat()
            )
        )

        connection.commit()

        return {
            "success": True,
            "status": "password_created",
            "message": "Your new password has been saved securely."
        }

    except sqlite3.Error as error:

        connection.rollback()

        return {
            "success": False,
            "message": f"Database error: {error}"
        }

    finally:
        connection.close()


# ==================================================
# VERIFY PASSWORD
# ==================================================

def verify_password(employee_id, password):

    connection = get_password_connection()

    try:

        row = connection.execute(
            """
            SELECT salt, password_hash
            FROM employee_credentials
            WHERE employee_id = ?
            """,
            (employee_id,)
        ).fetchone()

        if not row:
            return {
                "success": False,
                "message": "No password is configured for this employee."
            }

        candidate_hash = hash_password(
            password,
            row["salt"]
        )

        if not hmac.compare_digest(
            candidate_hash,
            row["password_hash"]
        ):
            return {
                "success": False,
                "message": "Password is incorrect."
            }

        return {
            "success": True,
            "message": "Password verified successfully."
        }

    finally:
        connection.close()


# ==================================================
# CHANGE PASSWORD
# ==================================================

def change_password(
    employee_id,
    current_password,
    new_password
):

    verification = verify_password(
        employee_id,
        current_password
    )

    if not verification["success"]:
        return verification

    if hmac.compare_digest(
        current_password.encode("utf-8"),
        new_password.encode("utf-8")
    ):
        return {
            "success": False,
            "message": "New password must be different from the current password."
        }

    return set_password(
        employee_id,
        new_password
    )


# ==================================================
# LEGACY AGENT COMPATIBILITY
# ==================================================

def reset_password(employee_id, approved=False):

    return {
        "success": False,
        "status": "password_form_required",
        "employee_id": employee_id,
        "message": (
            "Please use the employee portal password creation form."
        )
    }


# ==================================================
# OTHER IT SUPPORT TOOLS
# ==================================================

def check_vpn_status(employee_id):

    return {
        "success": True,
        "status": "simulated",
        "employee_id": employee_id,
        "message": "VPN status check simulated successfully."
    }


def install_software(
    employee_id,
    software_name,
    approved=False
):

    if not approved:
        return {
            "success": False,
            "status": "approval_required",
            "message": "Manager and IT approval are required."
        }

    return {
        "success": True,
        "status": "simulated",
        "employee_id": employee_id,
        "software_name": software_name,
        "message": (
            f"Installation of {software_name} was simulated. "
            "No software was actually installed."
        )
    }


def request_access(
    employee_id,
    system_name,
    approved=False
):

    if not approved:
        return {
            "success": False,
            "status": "approval_required",
            "message": "Manager and IT approval are required."
        }

    return {
        "success": True,
        "status": "simulated",
        "employee_id": employee_id,
        "system_name": system_name,
        "message": (
            f"Access request for {system_name} was simulated. "
            "No real access permissions were changed."
        )
    }
