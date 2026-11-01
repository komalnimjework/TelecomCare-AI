
import streamlit as st
import requests

from tools.it_tools import set_password

API_URL = "http://127.0.0.1:8000"


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="TelecomCare AI - Employee",
    page_icon="🎫",
    layout="wide"
)


# ==================================================
# 2. HELPER FUNCTIONS
# ==================================================

def is_password_reset_request(description, category):

    text = description.lower().strip()
    category = str(category or "").lower().strip()

    password_keywords = [
        "forgot password",
        "forget password",
        "reset password",
        "reset my password",
        "password reset",
        "change my password",
        "unable to login",
        "unable to log in",
        "cannot login",
        "cannot log in",
        "can't login",
        "can't log in",
        "locked out of my account",
        "password is not working"
    ]

    if "password" in category:
        return True

    return any(keyword in text for keyword in password_keywords)


# ==================================================
# 3. PAGE HEADER
# ==================================================

st.title("🎫 TelecomCare AI")
st.subheader("Employee IT Support Portal")

st.write(
    "Submit your IT issue and let the AI assistant "
    "classify, analyze and process your request."
)

st.divider()


# ==================================================
# 4. EMPLOYEE DETAILS
# ==================================================

st.header("1. Employee Details")

employee_id = st.text_input(
    "Employee ID",
    value="EMP001",
    max_chars=30
).strip()


# ==================================================
# 5. SUBMIT IT REQUEST
# ==================================================

st.header("2. Submit an IT Request")

description = st.text_area(
    "Describe your IT issue or request",
    placeholder=(
        "Example: I need Visual Studio Code installed "
        "on my laptop."
    ),
    height=120,
    max_chars=1000
)


if st.button(
    "Submit IT Request",
    type="primary",
    use_container_width=True
):

    if len(employee_id) < 3:

        st.error("Please enter a valid Employee ID.")

    elif len(description.strip()) < 5:

        st.error("Please enter a valid IT request.")

    else:

        st.session_state.pop("last_result", None)
        st.session_state.pop("tracked_ticket", None)

        st.session_state["show_password_form"] = False
        st.session_state["password_reset_success"] = False
        st.session_state["last_request_was_password"] = False

        with st.spinner("AI Agent is analyzing your request..."):

            try:

                from agents.it_agent import run_agent

                result = run_agent(
                    question=description.strip(),
                    employee_id=employee_id,
                    identity_verified=False
                )

                st.session_state["last_result"] = result
                st.session_state["last_employee_id"] = employee_id

                password_request = is_password_reset_request(
                    description,
                    result.get("category")
                )

                st.session_state["last_request_was_password"] = (
                    password_request
                )

                st.session_state["show_password_form"] = (
                    password_request
                )

                st.success("Your request has been processed.")

            except Exception as error:

                st.error(
                    f"Request processing failed: {error}"
                )


# ==================================================
# 6. EMPLOYEE-FRIENDLY REQUEST STATUS
# ==================================================

if "last_result" in st.session_state:

    result = st.session_state["last_result"]

    is_password_request = st.session_state.get(
        "last_request_was_password",
        False
    )

    st.divider()
    st.header("3. Request Status")

    if is_password_request:

        if not st.session_state.get(
            "password_reset_success", False
        ):

            st.info(
                "Your password reset request has been received. "
                "Please create your new password below."
            )

    else:

        assistant_response = result.get(
            "final_response",
            result.get(
                "response",
                "Your IT request has been received successfully."
            )
        )

        st.markdown(assistant_response)

        if result.get("ticket_id"):

            st.success(
                f"Your Ticket Number: {result.get('ticket_id')}"
            )

            st.info(
                "Save this ticket number to track your request."
            )

        if result.get("guardrail_blocked"):

            st.warning(
                "Your request needs further review "
                "by the IT support team."
            )


# ==================================================
# 7. CONDITIONAL PASSWORD RESET
# ==================================================

if st.session_state.get("show_password_form", False):

    st.divider()

    st.header("4. Reset Your Password")

    st.write(
        "Create a new password for your employee account."
    )

    st.info(
        "Password requirements: minimum 12 characters, "
        "at least one uppercase letter, one lowercase letter, "
        "one number and one special character."
    )

    with st.form("password_reset_form"):

        new_password = st.text_input(
            "New Password",
            type="password"
        )

        confirm_password = st.text_input(
            "Confirm New Password",
            type="password"
        )

        reset_clicked = st.form_submit_button(
            "Reset Password",
            use_container_width=True
        )

    if reset_clicked:

        if len(employee_id) < 3:

            st.error("Please enter a valid Employee ID.")

        elif not new_password or not confirm_password:

            st.error(
                "Please enter and confirm your new password."
            )

        elif new_password != confirm_password:

            st.error(
                "New password and confirmation do not match."
            )

        else:

            try:

                password_result = set_password(
                    employee_id=employee_id,
                    new_password=new_password
                )

                if password_result.get("success"):

                    st.session_state["show_password_form"] = False

                    st.session_state["password_reset_success"] = True

                    st.rerun()

                else:

                    st.error(
                        password_result.get(
                            "message",
                            "Password reset failed."
                        )
                    )

            except Exception as error:

                st.error(
                    f"Password reset failed: {error}"
                )


# ==================================================
# 8. PASSWORD RESET SUCCESS
# ==================================================

if st.session_state.get("password_reset_success", False):

    st.success(
        "Your password has been reset successfully "
        "and stored securely."
    )


# ==================================================
# 9. TRACK IT REQUEST
# ==================================================

st.divider()

st.header("5. Track Your IT Request")

st.write(
    "Enter your ticket number to check the status "
    "of your IT request."
)

track_ticket_id = st.text_input(
    "Ticket Number",
    placeholder="TC-2026-0003",
    key="track_ticket"
).strip()


if st.button(
    "Track Ticket",
    use_container_width=True
):

    if len(employee_id) < 3:

        st.error("Please enter your Employee ID first.")

    elif not track_ticket_id:

        st.warning("Please enter your ticket number.")

    else:

        with st.spinner("Fetching ticket details..."):

            try:

                response = requests.get(
                    f"{API_URL}/tickets/{track_ticket_id}",
                    params={
                        "employee_id": employee_id
                    },
                    timeout=10
                )

                if response.status_code == 200:

                    st.session_state["tracked_ticket"] = (
                        response.json()
                    )

                elif response.status_code == 403:

                    st.session_state.pop(
                        "tracked_ticket",
                        None
                    )

                    st.error(
                        "Access denied. This ticket does not "
                        "belong to the entered Employee ID."
                    )

                elif response.status_code == 404:

                    st.session_state.pop(
                        "tracked_ticket",
                        None
                    )

                    st.error("Ticket not found.")

                else:

                    st.session_state.pop(
                        "tracked_ticket",
                        None
                    )

                    st.error(
                        f"API Error: {response.text}"
                    )

            except requests.RequestException as error:

                st.error(
                    f"Backend connection failed: {error}"
                )


# ==================================================
# 10. DISPLAY EMPLOYEE TICKET DETAILS
# ==================================================

if "tracked_ticket" in st.session_state:

    ticket = st.session_state["tracked_ticket"]

    status = ticket.get("status", "UNKNOWN")

    status_messages = {

        "PENDING_MANAGER":
            "Your request is waiting for manager approval",

        "PENDING_IT":
            "Approved by Manager. Your request is now pending IT approval.",

        "APPROVED":
            "Your request has been approved",

        "EXECUTING":
            "Your request has passed both approvals and is being processed",

        "COMPLETED":
            "Your IT request has been completed",

        "FAILED":
            "Your IT request could not be completed",

        "REJECTED_BY_MANAGER":
            "Your request was not approved by the manager",

        "REJECTED_BY_IT":
            "Your request was not approved by the IT team",

        "SELF_SERVICE":
            "Self-service request",

        "AUTO_RESOLVED":
            "Your request has been resolved"
    }

    st.divider()

    st.subheader("Your Ticket Details")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Ticket Number",
            ticket.get("ticket_id", "N/A")
        )

    with col2:

        st.metric(
            "Request Status",
            status_messages.get(status, "Being processed")
        )

    st.write(
        f"**Employee ID:** {ticket.get('employee_id')}"
    )

    st.write(
        f"**Description:** {ticket.get('description')}"
    )

    # Internal category, priority and approver details
    # remain hidden from the employee portal.

    if status == "COMPLETED":

        st.success(
            "Your IT request has been completed successfully."
        )

    elif status == "PENDING_MANAGER":

        st.info(
            "Your request is waiting for manager approval."
        )

    elif status == "PENDING_IT":

        st.success(
            "Manager approval completed successfully."
        )

        st.info(
            "Your request is now waiting for the IT team's approval."
        )

    elif status == "EXECUTING":

        st.info(
            "Both approvals have been completed. "
            "Your IT request is being processed."
        )

    elif status in [
        "REJECTED_BY_MANAGER",
        "REJECTED_BY_IT"
    ]:

        st.error(
            "Your request could not be approved. "
            "Please contact the IT support team for assistance."
        )

    elif status == "FAILED":

        st.error(
            "Your IT request could not be completed. "
            "Please contact the IT support team."
        )

    elif status == "AUTO_RESOLVED":

        st.success(
            "Your request has been resolved."
        )


# ==================================================
# 11. FOOTER
# ==================================================

st.divider()

st.caption(
    "TelecomCare AI | Agentic IT Support Demonstration"
)
