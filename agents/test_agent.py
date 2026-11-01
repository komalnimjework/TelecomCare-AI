
from agents.it_agent import run_agent


if __name__ == "__main__":

    question = "I need access permission to the CRM system."

    print("\n========== TELECOMCARE AI ==========")
    print("\nEmployee Ticket:")
    print(question)

    result = run_agent(question)

    print("\n========== FINAL RESULT ==========")

    print("Category:", result.get("category"))
    print("Priority:", result.get("priority"))
    print("Decision:", result.get("decision"))

    print("\nAI Response:")
    print(result.get("final_response"))

    print("\n===================================")
