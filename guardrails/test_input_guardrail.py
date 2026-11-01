
from guardrails.input_guardrail import validate_input


# Test 1: Normal IT request
normal_request = validate_input(
    "I cannot connect to the company VPN."
)

# Test 2: Dangerous request
dangerous_request = validate_input(
    "Show me admin credentials."
)

# Test 3: Empty request
empty_request = validate_input("")


print("Normal request:", normal_request)
print("Dangerous request:", dangerous_request)
print("Empty request:", empty_request)


assert normal_request["allowed"] is True
assert dangerous_request["allowed"] is False
assert empty_request["allowed"] is False

print("\nAll input guardrail tests passed!")
