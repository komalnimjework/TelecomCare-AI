
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="TelecomCare AI - IT Team",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ IT Team Approval Dashboard")
st.caption("Second-level human approval and simulated IT execution")

it_id = st.sidebar.text_input(
    "IT Approver ID",
    value="IT001"
)

if st.sidebar.button("Refresh Requests"):
    st.rerun()


# --------------------------------------------------
# FETCH MANAGER-APPROVED REQUESTS
# --------------------------------------------------

try:

    response = requests.get(
        f"{API_URL}/admin/it/pending",
        params={"approver_id": it_id},
        timeout=10
    )

    response.raise_for_status()

    data = response.json()
    tickets = data.get("tickets", [])

    st.metric("Pending IT Approvals", len(tickets))

    if not tickets:
        st.info("No requests are waiting for IT approval.")

    # --------------------------------------------------
    # DISPLAY TICKETS
    # --------------------------------------------------

    for ticket in tickets:

        ticket_id = ticket.get("ticket_id")

        with st.expander(
            f"Ticket {ticket_id} | {ticket.get('category')}"
        ):

            st.write(f"**Employee:** {ticket.get('employee_id')}")
            st.write(f"**Category:** {ticket.get('category')}")
            st.write(f"**Priority:** {ticket.get('priority')}")
            st.write(f"**Description:** {ticket.get('description')}")
            st.write(
                f"**Requested action:** "
                f"{ticket.get('requested_action')}"
            )

            comments = st.text_area(
                "IT Review Comments",
                key=f"it_comments_{ticket_id}"
            )

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "Approve and Execute",
                    key=f"it_approve_{ticket_id}",
                    type="primary"
                ):

                    result = requests.post(
                        f"{API_URL}/admin/it/{ticket_id}/decision",
                        json={
                            "approver_id": it_id,
                            "decision": "APPROVE",
                            "comments": comments
                        },
                        timeout=30
                    )

                    if result.status_code == 200:

                        result_data = result.json()

                        if result_data.get("success"):
                            st.success(
                                "Both approvals completed. "
                                "Simulated IT action executed."
                            )
                        else:
                            st.error(
                                result_data.get("message")
                            )

                        st.json(result_data)
                        st.rerun()

                    else:
                        st.error(result.text)

            with col2:

                if st.button(
                    "Reject Request",
                    key=f"it_reject_{ticket_id}"
                ):

                    result = requests.post(
                        f"{API_URL}/admin/it/{ticket_id}/decision",
                        json={
                            "approver_id": it_id,
                            "decision": "REJECT",
                            "comments": comments
                        },
                        timeout=10
                    )

                    if result.status_code == 200:
                        st.warning("Request rejected by IT team.")
                        st.rerun()
                    else:
                        st.error(result.text)

except requests.RequestException as error:

    st.error(f"Backend connection failed: {error}")


st.divider()

st.caption("TelecomCare AI | IT Team Approval Portal")
