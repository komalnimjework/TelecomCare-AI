
"""
Browser-based human approval workflow.

Does not ask for terminal input.
Returns pending status until a human decision is provided.
"""


def request_human_approval(
    action: str,
    employee_id: str,
    decision: str = None
) -> dict:
    """
    Process human approval.

    decision=None:
        Return pending approval.

    decision='yes':
        Approve the action.

    decision='no':
        Reject the action.
    """

    if decision is None:

        return {
            "approved": False,
            "action": action,
            "employee_id": employee_id,
            "status": "pending",
            "message": "Waiting for human approval."
        }

    approved = decision.strip().lower() == "yes"

    return {
        "approved": approved,
        "action": action,
        "employee_id": employee_id,
        "status": "approved" if approved else "rejected",
        "message": (
            "Action approved."
            if approved
            else "Action rejected by the human approver."
        )
    }
