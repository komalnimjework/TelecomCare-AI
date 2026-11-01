
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from database.db import (
    get_ticket,
    get_pending_approvals,
    record_approval,
    update_ticket_status,
    get_approval_history,
    record_action,
)

from tools.action_executor import execute_it_action


router = APIRouter(
    prefix="/admin",
    tags=["Approval Management"]
)


# --------------------------------------------------
# REQUEST MODEL
# --------------------------------------------------

class ApprovalRequest(BaseModel):
    approver_id: str
    decision: str
    comments: Optional[str] = ""


def validate_decision(decision: str):

    decision = decision.upper()

    if decision not in ["APPROVE", "REJECT"]:
        raise HTTPException(
            status_code=400,
            detail="Decision must be APPROVE or REJECT"
        )

    return decision


# --------------------------------------------------
# MANAGER DASHBOARD - PENDING REQUESTS
# --------------------------------------------------

@router.get("/manager/pending")
def manager_pending_requests(approver_id: str = "MGR001"):

    tickets = get_pending_approvals(
        "MANAGER",
        approver_id
    )

    return {
        "success": True,
        "approver_id": approver_id,
        "total_pending": len(tickets),
        "tickets": tickets
    }


# --------------------------------------------------
# MANAGER APPROVAL DECISION
# --------------------------------------------------

@router.post("/manager/{ticket_id}/decision")
def manager_decision(
    ticket_id: str,
    request: ApprovalRequest
):

    ticket = get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if ticket["manager_id"] != request.approver_id:
        raise HTTPException(
            status_code=403,
            detail="Ticket is not assigned to this manager"
        )

    if ticket["status"] != "PENDING_MANAGER":
        raise HTTPException(
            status_code=400,
            detail="Ticket is not waiting for manager approval"
        )

    decision = validate_decision(request.decision)

    record_approval(
        ticket_id,
        "MANAGER",
        request.approver_id,
        decision,
        request.comments or ""
    )

    if decision == "APPROVE":

        update_ticket_status(
            ticket_id,
            "PENDING_IT",
            ticket["it_approver_id"]
        )

        message = "Manager approved. Forwarded to IT team."

    else:

        update_ticket_status(
            ticket_id,
            "REJECTED_BY_MANAGER",
            None
        )

        message = "Manager rejected the request."

    return {
        "success": True,
        "ticket_id": ticket_id,
        "decision": decision,
        "message": message
    }


# --------------------------------------------------
# IT DASHBOARD - PENDING REQUESTS
# --------------------------------------------------

@router.get("/it/pending")
def it_pending_requests(approver_id: str = "IT001"):

    tickets = get_pending_approvals(
        "IT",
        approver_id
    )

    return {
        "success": True,
        "approver_id": approver_id,
        "total_pending": len(tickets),
        "tickets": tickets
    }


# --------------------------------------------------
# IT APPROVAL + ACTION EXECUTION
# --------------------------------------------------

@router.post("/it/{ticket_id}/decision")
def it_decision(
    ticket_id: str,
    request: ApprovalRequest
):

    ticket = get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    if ticket["it_approver_id"] != request.approver_id:
        raise HTTPException(
            status_code=403,
            detail="Ticket is not assigned to this IT approver"
        )

    if ticket["status"] != "PENDING_IT":
        raise HTTPException(
            status_code=400,
            detail="Ticket is not waiting for IT approval"
        )

    # Verify manager approval
    history = get_approval_history(ticket_id)

    manager_approved = any(
        item["approval_stage"] == "MANAGER"
        and item["decision"] == "APPROVE"
        for item in history
    )

    if not manager_approved:
        raise HTTPException(
            status_code=403,
            detail="Manager approval is required first"
        )

    decision = validate_decision(request.decision)

    record_approval(
        ticket_id,
        "IT",
        request.approver_id,
        decision,
        request.comments or ""
    )

    # Stop if IT rejects the request
    if decision == "REJECT":

        update_ticket_status(
            ticket_id,
            "REJECTED_BY_IT",
            None
        )

        record_action(
            ticket_id,
            ticket["category"],
            "REJECTED",
            "Rejected by IT team"
        )

        return {
            "success": True,
            "ticket_id": ticket_id,
            "decision": decision,
            "status": "REJECTED_BY_IT",
            "message": "IT team rejected the request."
        }

    # Mark as executing to prevent repeated approval requests
    update_ticket_status(
        ticket_id,
        "EXECUTING",
        None
    )

    # Map ticket category to supported action
    action_mapping = {
        "Software Installation": "software_installation",
        "Access Request": "access_request"
    }

    action = action_mapping.get(ticket["category"])

    if not action:

        update_ticket_status(
            ticket_id,
            "FAILED",
            None
        )

        record_action(
            ticket_id,
            ticket["category"],
            "FAILED",
            "Unsupported ticket category"
        )

        raise HTTPException(
            status_code=400,
            detail="Unsupported IT action"
        )

    # Execute only after both approval records exist
    result = execute_it_action(
        action=action,
        employee_id=ticket["employee_id"],
        software_name=ticket["requested_action"] or "Requested software",
        system_name=ticket["requested_action"] or "Requested system",
        dual_approval_verified=True
    )

    # Record execution result
    execution_success = result.get("success", False)

    final_status = (
        "COMPLETED"
        if execution_success
        else "FAILED"
    )

    update_ticket_status(
        ticket_id,
        final_status,
        None
    )

    record_action(
        ticket_id,
        action,
        final_status,
        result.get("message", "")
    )

    return {
        "success": execution_success,
        "ticket_id": ticket_id,
        "decision": "APPROVE",
        "status": final_status,
        "execution_result": result,
        "message": (
            "Both approvals completed and simulated action executed."
            if execution_success
            else "Approval completed, but action execution failed."
        )
    }


# --------------------------------------------------
# APPROVAL HISTORY
# --------------------------------------------------

@router.get("/tickets/{ticket_id}/history")
def ticket_approval_history(ticket_id: str):

    ticket = get_ticket(ticket_id)

    if not ticket:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found"
        )

    return {
        "success": True,
        "ticket_id": ticket_id,
        "approval_history": get_approval_history(ticket_id)
    }
