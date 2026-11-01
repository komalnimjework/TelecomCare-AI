
"""
Audit logger for TelecomCare-AI.

Records simulated IT action requests and their outcomes.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


LOG_FILE = Path("logs/it_action_audit.jsonl")


def log_it_action(
    employee_id: str,
    action: str,
    approval_status: str,
    execution_status: str
):
    """Append one audit event to a JSON Lines file."""

    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    audit_record = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "employee_id": employee_id,
        "action": action,
        "approval_status": approval_status,
        "execution_status": execution_status
    }

    with LOG_FILE.open("a", encoding="utf-8") as file:
        file.write(json.dumps(audit_record) + "\n")

    return audit_record
