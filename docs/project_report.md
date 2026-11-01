# TelecomCare-AI
## Agentic AI-Based IT Ticket Automation System

### 1. Executive Summary

TelecomCare-AI is an AI-powered IT support automation MVP designed for a telecom organization. It helps employees submit IT support requests, receive AI-assisted troubleshooting guidance, and track their tickets.

The solution combines an AI agent, Retrieval-Augmented Generation (RAG), a local Large Language Model, and a human approval workflow to manage IT support requests.

### 2. Problem Statement

Traditional IT support processes often involve manual ticket creation, repetitive troubleshooting, and delays in handling software installation and access requests.

The objective of this project is to demonstrate how Agentic AI can streamline IT support workflows, provide knowledge-based troubleshooting, and introduce controlled automation with human approval.

### 3. Project Objectives

- Provide a simple employee IT support portal.
- Automatically classify IT requests and assign priority.
- Answer troubleshooting questions using an internal knowledge base.
- Create and track IT support tickets.
- Implement manager and IT approval workflows.
- Simulate approved IT actions.
- Maintain performance metrics and action audit logs.
- Apply basic input and output guardrails.

### 4. Proposed Solution

The application provides three portals:

**Employee Portal**
- Submit IT issues and service requests.
- Receive AI-generated troubleshooting responses.
- Submit password reset requests through a dedicated workflow.
- Track ticket status.

**Manager Portal**
- Review software installation and access requests.
- Approve or reject employee requests.

**IT Administrator Portal**
- Review manager-approved requests.
- Approve or reject IT actions.
- Trigger simulated actions after approval.

### 5. Technical Implementation

| Component | Implementation |
|---|---|
| Backend | FastAPI |
| Frontend | Streamlit |
| Agent Orchestration | LangGraph |
| LLM | Ollama – Qwen 2.5 1.5B |
| Embeddings | all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Relational Database | SQLite |
| Programming Language | Python |

### 6. AI Agent Workflow

The LangGraph-based agent coordinates the IT support workflow.

1. Receive the employee request.
2. Validate input using the input guardrail.
3. Classify the request and determine priority.
4. Retrieve relevant knowledge-base documents when troubleshooting is required.
5. Generate an answer using the local LLM.
6. Validate the generated response using the output guardrail.
7. Respond to the employee, reject unsafe input, or create a ticket.
8. Route sensitive requests through the required approval workflow.

### 7. Retrieval-Augmented Generation

The RAG implementation uses Sentence Transformers to generate embeddings and ChromaDB for semantic retrieval.

The system retrieves relevant IT knowledge-base articles and supplies them as context to the local LLM.

The generated response includes the names of retrieved source documents to improve traceability.

### 8. Human-in-the-Loop Approval

Software installation and access requests follow a two-stage approval process.

- Stage 1: Manager approval.
- Stage 2: IT administrator approval.
- Stage 3: Simulated IT action after both approvals.

Rejected requests do not proceed to action execution.

### 9. Security and Guardrails

The MVP implements:
- Basic prompt-injection and unsafe-input checks.
- Detection of selected sensitive information patterns.
- Output validation for selected unsafe credential requests and unsupported completion claims.
- PBKDF2-HMAC-SHA256 password hashing with random salts.
- Approval validation before simulated sensitive actions.
- Audit logging of simulated actions.

The password reset workflow is a demonstration and does not verify employee identity or change a real company account.

### 10. Testing and Evaluation

The classification evaluation used 10 synthetic test cases.

| Metric | Result |
|---|---:|
| Test Cases | 10 |
| Correct Predictions | 10 |
| Overall Accuracy | 100% |
| Category Accuracy | 100% |
| Priority Accuracy | 100% |

**Evaluation note:** These results are from a small synthetic dataset and should not be interpreted as production-level model performance.

Functional testing also covered:
- Software installation request and dual approval.
- Application access request and dual approval.
- Manager rejection workflow.
- VPN troubleshooting using RAG.
- Password reset demonstration.
- Input and output guardrail checks.

### 11. Performance and Cost Optimization

The solution uses local Ollama inference and local embeddings instead of paid external model APIs.

Performance logs capture retrieval latency, LLM latency, total processing time, token usage when available, and external API cost.

External model API cost is zero for the current local inference workflow. Local hardware and electricity costs are not included.

### 12. Limitations

- IT actions are simulated; no real software installation or access provisioning occurs.
- Password reset does not integrate with enterprise identity systems.
- Classification evaluation uses only 10 synthetic examples.
- Guardrails are basic rule-based checks.
- The knowledge base contains a limited set of IT troubleshooting articles.
- The current MVP does not provide production-grade authentication or authorization.

### 13. Future Enhancements

- Integrate enterprise SSO and identity verification.
- Connect to real IT service management platforms.
- Integrate approved endpoint management and access provisioning tools.
- Expand the knowledge base and evaluation dataset.
- Implement stronger role-based access control.
- Improve security monitoring and guardrail coverage.

### 14. Conclusion

TelecomCare-AI demonstrates how Agentic AI, RAG, local LLM inference, and human approval workflows can be combined to automate parts of an IT support process.

The MVP provides a foundation for intelligent ticket classification, knowledge-based troubleshooting, ticket tracking, and controlled IT action workflows.