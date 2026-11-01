
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TelecomCare AI - Manager",
    page_icon="👨‍💼",
    layout="wide"
)

st.title("👨‍💼 Manager Approval Dashboard")
st.caption("First-level human approval")

manager_id = st.sidebar.text_input(
    "Manager ID",
    value="MGR001"
)

if st.sidebar.button("Refresh Requests"):
    st.rerun()

# --------------------------------------------------
# FETCH PENDING REQUESTS
# --------------------------------------------------

try:
    response = requests.get(
        f"{API_URL}/admin/manager/pending",
        params={"approver_id": manager_id},
        timeout=10
    )

    response.raise_for_status()
    data = response.json()

    tickets = data.get("tickets", [])

    st.metric("Pending Approvals", len(tickets))

    if not tickets:
        st.info("No requests are waiting for your approval.")

    # --------------------------------------------------
    # DISPLAY EACH TICKET
    # --------------------------------------------------

    for ticket in tickets:

        ticket_id = ticket.get("ticket_id", "Unknown")

        with st.expander(
            f"Ticket {ticket_id} | {ticket.get('category', '')}"
        ):

            st.write(f"**Employee:** {ticket.get('employee_id')}")
            st.write(f"**Priority:** {ticket.get('priority')}")
            st.write(f"**Description:** {ticket.get('description')}")
            st.write(
                f"**Requested action:** "
                f"{ticket.get('requested_action')}"
            )
            st.write(
                f"**Business justification:** "
                f"{ticket.get('business_justification')}"
            )

            comments = st.text_area(
                "Manager comments",
                key=f"manager_comments_{ticket_id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Approve Request",
                    key=f"approve_{ticket_id}",
                    type="primary"
                ):

                    result = requests.post(
                        f"{API_URL}/admin/manager/{ticket_id}/decision",
                        json={
                            "approver_id": manager_id,
                            "decision": "APPROVE",
                            "comments": comments
                        },
                        timeout=10
                    )

                    if result.status_code == 200:
                        st.success(
                            "Approved! Forwarded to IT team."
                        )
                        st.rerun()
                    else:
                        st.error(result.text)

            with col2:

                if st.button(
                    "Reject Request",
                    key=f"reject_{ticket_id}"
                ):

                    result = requests.post(
                        f"{API_URL}/admin/manager/{ticket_id}/decision",
                        json={
                            "approver_id": manager_id,
                            "decision": "REJECT",
                            "comments": comments
                        },
                        timeout=10
                    )

                    if result.status_code == 200:
                        st.warning("Request rejected.")
                        st.rerun()
                    else:
                        st.error(result.text)

except requests.RequestException as error:

    st.error(f"Cannot connect to backend: {error}")

st.divider()

st.caption("TelecomCare AI | Manager Approval Portal")
