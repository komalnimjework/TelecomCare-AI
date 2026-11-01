
"""
Central action executor for TelecomCare AI.

Password reset:
- Self-service after identity verification.
- No human approval required.

Software installation and access request:
- Requires manager approval AND IT approval.
- Executes only after backend verifies both approvals.

All operations are simulated locally.
"""

from tools.it_tools import (
    reset_password,
    install_software,
    request_access
)

from tools.audit_logger import log_it_action


def execute_it_action(
    action: str,
    employee_id: str,
    software_name: str = "",
    system_name: str = "",
    identity_verified: bool = False,
    approval_decision: str = None,
    dual_approval_verified: bool = False
) -> dict:

    # --------------------------------------------------
    # 1. PASSWORD RESET - SELF SERVICE
    # --------------------------------------------------

    if action == "password_reset":

        if not identity_verified:

            log_it_action(
                employee_id=employee_id,
                action=action,
                approval_status="not_required",
                execution_status="verification_required"
            )

            return {
                "success": False,
                "status": "verification_required",
                "message": "Identity verification is required."
            }

        result = reset_password(
            employee_id,
            approved=True
        )

        log_it_action(
            employee_id=employee_id,
            action=action,
            approval_status="not_required",
            execution_status=result.get("status", "unknown")
        )

        return result

    # --------------------------------------------------
    # 2. SOFTWARE INSTALLATION / ACCESS REQUEST
    # --------------------------------------------------

    if action in ["software_installation", "access_request"]:

        # Never execute sensitive actions without
        # backend verification of both approval stages.

        if not dual_approval_verified:

            log_it_action(
                employee_id=employee_id,
                action=action,
                approval_status="not_verified",
                execution_status="blocked"
            )

            return {
                "success": False,
                "status": "approval_required",
                "message": (
                    "Both manager and IT approvals are required "
                    "before executing this action."
                )
            }

        # ----------------------------------------------
        # Execute only after both approvals are verified
        # ----------------------------------------------

        if action == "software_installation":

            result = install_software(
                employee_id,
                software_name,
                approved=True
            )

        else:

            result = request_access(
                employee_id,
                system_name,
                approved=True
            )

        # ----------------------------------------------
        # Record execution in audit log
        # ----------------------------------------------

        log_it_action(
            employee_id=employee_id,
            action=action,
            approval_status="manager_and_it_approved",
            execution_status=result.get("status", "unknown")
        )

        return result

    # --------------------------------------------------
    # 3. UNSUPPORTED ACTION
    # --------------------------------------------------

    return {
        "success": False,
        "status": "unsupported",
        "message": "This IT action is not supported."
    }
