
from tools.action_executor import execute_it_action


# Test 1: Software installation approved
approved_result = execute_it_action(
    action="software_installation",
    employee_id="EMP001",
    software_name="Microsoft Teams",
    approver_input=lambda message: "yes"
)

print("\nApproved action:", approved_result)


# Test 2: Access request rejected
rejected_result = execute_it_action(
    action="access_request",
    employee_id="EMP002",
    system_name="CRM System",
    approver_input=lambda message: "no"
)

print("\nRejected action:", rejected_result)


assert approved_result["status"] == "simulated"
assert rejected_result["status"] == "rejected"

print("\nAll action executor tests passed!")
