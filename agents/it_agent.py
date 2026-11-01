
import re
from typing import TypedDict, Optional

from langgraph.graph import StateGraph, START, END

from rag.answer_generator import generate_rag_answer
from guardrails.input_guardrail import validate_input
from tools.action_executor import execute_it_action
from database.db import create_ticket


# ==================================================
# 1. AGENT STATE
# ==================================================

class TicketState(TypedDict, total=False):
    question: str
    employee_id: str
    category: str
    priority: str

    rag_result: dict
    final_response: str

    decision: str
    ticket_id: str

    guardrail_blocked: bool
    input_blocked: bool
    input_guardrail_reason: str

    identity_verified: bool
    approval_decision: Optional[str]

    # Password reset fields
    temporary_password: str
    must_change_password: bool


# ==================================================
# 2. INPUT GUARDRAIL
# ==================================================

def check_input_guardrail(state: TicketState):

    result = validate_input(state["question"])

    return {
        "input_blocked": not result["allowed"],
        "input_guardrail_reason": result["reason"]
    }


def reject_unsafe_input(state: TicketState):

    return {
        "final_response": (
            "Your request was blocked by the security guardrail. "
            "Please submit a valid IT support request."
        ),
        "decision": "blocked"
    }


def route_input(state: TicketState):

    if state.get("input_blocked", False):
        return "reject"

    return "continue"


# ==================================================
# 3. TICKET CLASSIFICATION
# ==================================================

def classify_ticket(state: TicketState):

    question = state["question"].lower()

    general_words = [
        "general inquiry",
        "software information",
        "documentation",
        "how to use",
        "feature request",
        "suggestion"
    ]

    if any(word in question for word in [
        "vpn", "virtual private network"
    ]):
        category = "VPN"

    elif any(word in question for word in [
        "password", "login", "locked account"
    ]):
        category = "Password"

    elif any(word in question for word in [
        "access", "permission", "authorization"
    ]):
        category = "Access Request"

    elif any(word in question for word in [
        "network", "internet", "wifi", "connectivity"
    ]):
        category = "Network"

    elif any(word in question for word in general_words):
        category = "General IT"

    elif any(word in question for word in [
        "install", "software", "application"
    ]):
        category = "Software Installation"

    else:
        category = "General IT"

    # Priority classification

    critical_words = [
        "company-wide outage",
        "entire network down",
        "entire company network is down",
        "complete network failure",
        "all users affected",
        "telecom outage",
        "production environment down",
        "critical production outage",
        "data center outage",
        "business completely stopped",
        "critical infrastructure failure",
        "all services unavailable"
    ]

    high_words = [
        "urgent",
        "critical",
        "business stopped",
        "client meeting",
        "cannot work",
        "production down",
        "production server is down",
        "network server is down",
        "server is down",
        "multiple users affected",
        "multiple users are affected",
        "application unavailable",
        "system outage",
        "service disruption",
        "deadline today",
        "major performance issue",
        "payment system failure"
    ]

    low_words = [
        "general inquiry",
        "software information",
        "how to use",
        "feature request",
        "documentation request",
        "minor issue",
        "suggestion",
        "non-urgent request"
    ]

    if any(word in question for word in critical_words):
        priority = "Critical"

    elif any(word in question for word in high_words):
        priority = "High"

    elif any(word in question for word in low_words):
        priority = "Low"

    else:
        priority = "Medium"

    print("[AGENT] Category:", category)
    print("[AGENT] Priority:", priority)

    return {
        "category": category,
        "priority": priority
    }


# ==================================================
# 4. RAG RETRIEVAL
# ==================================================

def retrieve_solution(state: TicketState):

    print("[AGENT] Retrieving knowledge...")

    result = generate_rag_answer(state["question"])

    return {
        "rag_result": result
    }


# ==================================================
# 5. OUTPUT GUARDRAIL
# ==================================================

def validate_response(state: TicketState):

    result = state.get("rag_result", {})
    answer = result.get("answer", "")

    unsafe_phrases = [
        "share your password",
        "send your otp",
        "provide your one-time password"
    ]

    answer_lower = answer.lower()

    blocked = any(
        phrase in answer_lower
        for phrase in unsafe_phrases
    )

    completion_claims = [
        "password has been reset",
        "account has been unlocked",
        "software has been installed",
        "access has been granted"
    ]

    if any(
        phrase in answer_lower
        for phrase in completion_claims
    ):
        blocked = True

    if blocked:
        answer = (
            "The generated response failed a security check. "
            "No IT action has been executed. "
            "Please contact IT support."
        )

    return {
        "final_response": answer,
        "guardrail_blocked": blocked
    }


# ==================================================
# 6. DECISION NODE
# ==================================================

def decide_next_action(state: TicketState):

    result = state.get("rag_result", {})
    category = state.get("category")

    if state.get("guardrail_blocked", False):

        decision = "escalate"

    elif category == "Password":

        decision = "action"

    elif category in [
        "Software Installation",
        "Access Request"
    ]:

        decision = "action"

    elif state.get("priority") in ["High", "Critical"]:

        decision = "escalate"

    elif result.get("status") != "success":

        decision = "escalate"

    else:

        decision = "respond"

    print("[AGENT] Decision:", decision)

    return {
        "decision": decision
    }


# ==================================================
# 7. RESPONSE NODE
# ==================================================

def respond_to_employee(state: TicketState):

    return {
        "final_response": state["final_response"]
    }


# ==================================================
# 8. ESCALATION NODE
# ==================================================

def escalate_ticket(state: TicketState):

    message = (
        "Your issue requires additional IT support.\n"
        "Your request has been forwarded for IT support review.\n"
        "No privileged IT action was executed."
    )

    return {
        "final_response": message,
        "decision": "escalate"
    }


# ==================================================
# 9. HELPER: EXTRACT REQUESTED SOFTWARE OR SYSTEM
# ==================================================

def extract_requested_action(question: str, category: str):

    requested_action = ""
    question = question.strip()

    if category == "Software Installation":

        patterns = [
            r"\bneed\s+(.+?)\s+installed\b",
            r"\bwant\s+(.+?)\s+installed\b",
            r"\binstall\s+(?:the\s+)?(.+?)(?:\s+(?:on|in|for|because|so that|to)\b|[.!?]|$)",
            r"\binstallation of\s+(?:the\s+)?(.+?)(?:\s+(?:on|in|for|because|so that|to)\b|[.!?]|$)"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )

            if match:
                requested_action = match.group(1).strip()
                break

        requested_action = re.sub(
            r"\s+(?:software|application)$",
            "",
            requested_action,
            flags=re.IGNORECASE
        ).strip(" .,!?")

        if not requested_action:
            requested_action = "Software installation request"

    elif category == "Access Request":

        patterns = [
            r"\baccess\s+to\s+(.+?)(?:\s+because|\s+for|[.!?]|$)",
            r"\bpermission\s+to\s+access\s+(.+?)(?:\s+because|\s+for|[.!?]|$)",
            r"\baccess\s+for\s+(.+?)(?:\s+because|\s+for|[.!?]|$)"
        ]

        for pattern in patterns:
            match = re.search(
                pattern,
                question,
                re.IGNORECASE
            )

            if match:
                requested_action = match.group(1).strip()
                break

        requested_action = requested_action.strip(" .,!?")

        if not requested_action:
            requested_action = "System access request"

    return requested_action


# ==================================================
# 10. PASSWORD RESET AND TICKET CREATION
# ==================================================

def handle_sensitive_action(state: TicketState):

    category = state.get("category", "")
    employee_id = state.get("employee_id", "EMP001")
    question = state.get("question", "").strip()

    # Demo approver assignments
    manager_id = "MGR001"
    it_approver_id = "IT001"

    # --------------------------------------------------
    # PASSWORD RESET - SELF SERVICE
    # --------------------------------------------------

    if category == "Password":

        return {
            "final_response": (
                "Please use the password creation form below "
                "to set your new password."
            ),
            "decision": "password_form_required"
        }

    # --------------------------------------------------
    # SOFTWARE INSTALLATION / ACCESS REQUEST
    # --------------------------------------------------

    if category in [
        "Software Installation",
        "Access Request"
    ]:

        requested_action = extract_requested_action(
            question,
            category
        )

        print("[AGENT] Creating approval ticket...")
        print("[AGENT] Requested action:", requested_action)

        ticket_result = create_ticket(
            employee_id=employee_id,
            manager_id=manager_id,
            it_approver_id=it_approver_id,
            category=category,
            priority=state.get("priority", "Medium"),
            description=question,
            employee_name="Demo Employee",
            requested_action=requested_action,
            business_justification=(
                "Request submitted through TelecomCare AI. "
                "Manager and IT authorization are required."
            )
        )

        if not ticket_result.get("success"):

            return {
                "final_response": (
                    "Unable to create your IT ticket. "
                    "Please contact IT support."
                ),
                "decision": "error"
            }

        ticket_id = ticket_result["ticket_id"]

        print("[AGENT] Ticket created:", ticket_id)

        return {
            "ticket_id": ticket_id,
            "final_response": (
                "Your IT request has been submitted successfully.\n\n"
                f"**Ticket Number:** {ticket_id}\n\n"
                "**Current Status:** Pending Manager Approval\n\n"
                "After manager approval, your request will be "
                "forwarded to IT for the second approval.\n\n"
                "You can use your ticket number to track your request."
            ),
            "decision": "pending"
        }

    # --------------------------------------------------
    # OTHER REQUESTS
    # --------------------------------------------------

    return {
        "final_response": (
            "Your request requires review by IT support."
        ),
        "decision": "escalate"
    }


# ==================================================
# 11. CONDITIONAL ROUTING
# ==================================================

def route_decision(state: TicketState):

    if state["decision"] == "action":
        return "action"

    elif state["decision"] == "escalate":
        return "escalate"

    return "respond"


# ==================================================
# 12. BUILD LANGGRAPH WORKFLOW
# ==================================================

def build_agent():

    workflow = StateGraph(TicketState)

    workflow.add_node(
        "input_guardrail",
        check_input_guardrail
    )

    workflow.add_node(
        "reject_input",
        reject_unsafe_input
    )

    workflow.add_node(
        "classification",
        classify_ticket
    )

    workflow.add_node(
        "retrieval",
        retrieve_solution
    )

    workflow.add_node(
        "guardrails",
        validate_response
    )

    workflow.add_node(
        "decision",
        decide_next_action
    )

    workflow.add_node(
        "respond",
        respond_to_employee
    )

    workflow.add_node(
        "escalate",
        escalate_ticket
    )

    workflow.add_node(
        "action",
        handle_sensitive_action
    )

    workflow.add_edge(
        START,
        "input_guardrail"
    )

    workflow.add_conditional_edges(
        "input_guardrail",
        route_input,
        {
            "reject": "reject_input",
            "continue": "classification"
        }
    )

    workflow.add_edge("reject_input", END)

    workflow.add_edge("classification", "retrieval")
    workflow.add_edge("retrieval", "guardrails")
    workflow.add_edge("guardrails", "decision")

    workflow.add_conditional_edges(
        "decision",
        route_decision,
        {
            "respond": "respond",
            "escalate": "escalate",
            "action": "action"
        }
    )

    workflow.add_edge("respond", END)
    workflow.add_edge("escalate", END)
    workflow.add_edge("action", END)

    return workflow.compile()


# ==================================================
# 13. RUN AGENT
# ==================================================

def run_agent(
    question: str,
    identity_verified: bool = False,
    approval_decision: str = None,
    employee_id: str = "EMP001"
):

    if not employee_id or len(employee_id.strip()) < 3:
        raise ValueError("A valid employee ID is required.")

    agent = build_agent()

    initial_state = {
        "question": question,
        "employee_id": employee_id.strip(),

        "category": "",
        "priority": "",

        "rag_result": {},
        "final_response": "",

        "decision": "",
        "ticket_id": "",

        "guardrail_blocked": False,

        "input_blocked": False,
        "input_guardrail_reason": "",

        "identity_verified": identity_verified,
        "approval_decision": approval_decision,

        "temporary_password": "",
        "must_change_password": False
    }

    result = agent.invoke(initial_state)

    return result
