
from tools.human_approval import request_human_approval


# Test 1: Administrator approves
approval_result = request_human_approval(
    action="Install Microsoft Teams",
    employee_id="EMP001",
    approver_input=lambda message: "yes"
)

print("Approval result:", approval_result)


# Test 2: Administrator rejects
rejection_result = request_human_approval(
    action="Grant CRM access",
    employee_id="EMP002",
    approver_input=lambda message: "no"
)

print("Rejection result:", rejection_result)


assert approval_result["approved"] is True
assert approval_result["status"] == "approved"

assert rejection_result["approved"] is False
assert rejection_result["status"] == "rejected"

print("\nAll human approval tests passed!")
