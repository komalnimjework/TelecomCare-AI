
from tools.it_tools import (
    check_vpn_status,
    reset_password,
    install_software,
    request_access
)

# Test 1: VPN diagnostic (low-risk simulated action)
vpn_result = check_vpn_status("EMP001")
print("\nVPN Result:", vpn_result)

# Test 2: Password reset without approval
password_result = reset_password("EMP001")
print("\nPassword Reset Without Approval:", password_result)

# Test 3: Password reset with approval
approved_password_result = reset_password(
    "EMP001",
    approved=True
)
print("\nPassword Reset With Approval:", approved_password_result)

# Test 4: Software installation without approval
software_result = install_software(
    "EMP001",
    "Microsoft Teams"
)
print("\nSoftware Installation:", software_result)

# Test 5: Access request without approval
access_result = request_access(
    "EMP001",
    "CRM System"
)
print("\nAccess Request:", access_result)


assert vpn_result["success"] is True
assert password_result["status"] == "approval_required"
assert approved_password_result["status"] == "simulated"
assert software_result["status"] == "approval_required"
assert access_result["status"] == "approval_required"

print("\nAll IT tool tests passed!")
