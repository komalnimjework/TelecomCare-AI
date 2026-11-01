# TelecomCare AI

### Agentic AI-Based IT Ticket Automation System

TelecomCare AI is an Agentic AI-powered IT support automation platform designed to automate employee IT requests, intelligent ticket classification, knowledge-based troubleshooting, approval workflows, and IT action processing.

The system combines **LangGraph, Retrieval-Augmented Generation (RAG), local LLM inference, FastAPI, Streamlit, and SQLite** to provide an intelligent IT support experience while maintaining human approval for sensitive operations.

---

## 1. Project Objective

The objective is to build an AI-powered IT support assistant that can:

- Understand employee IT issues using natural language.
- Automatically classify requests and assign priority.
- Retrieve relevant troubleshooting information from a knowledge base.
- Generate contextual responses using a local LLM.
- Create IT tickets when human intervention is required.
- Manage manager and IT approval workflows.
- Execute simulated IT actions after required approvals.
- Maintain security guardrails, audit history, and performance metrics.

---

## 2. Technology Stack

| Component | Technology |
|---|---|
| Programming Language | Python 3.12 |
| Backend API | FastAPI |
| Frontend | Streamlit |
| Agent Orchestration | LangGraph |
| LLM | Qwen 2.5 1.5B via Ollama |
| Embedding Model | Sentence Transformers - all-MiniLM-L6-v2 |
| Vector Database | ChromaDB |
| Similarity Search | Cosine Similarity |
| Database | SQLite |
| ML Evaluation | Scikit-learn |
| Performance Monitoring | Custom JSONL logging |
| API Communication | REST APIs |

---

## 3. System Architecture

The application consists of three user interfaces connected to a shared backend and agent workflow.

### Employee Portal

- Submit IT support requests.
- Receive AI-generated troubleshooting guidance.
- Request password resets.
- Track ticket status.

### Manager Portal

- View assigned pending approval requests.
- Approve or reject software installation requests.
- Approve or reject application access requests.

### IT Admin Portal

- Review manager-approved requests.
- Provide the second approval.
- Trigger simulated IT actions.
- Record action execution status.

### AI Processing Architecture

1. Employee submits a request.
2. Input guardrail validates the request.
3. LangGraph agent classifies the issue.
4. Priority is assigned.
5. RAG retrieves relevant knowledge-base documents.
6. Local LLM generates a contextual response.
7. Output guardrail validates the generated response.
8. Agent decides whether to respond, escalate, or initiate an approval workflow.
9. SQLite stores ticket and approval information.
10. Audit logs capture simulated IT actions.

---

## 4. Key Features

### 4.1 Intelligent Ticket Classification

Automatically classifies employee requests into:

- VPN
- Network
- Password
- Software Installation
- Access Request
- General IT

Priority levels:

- Critical
- High
- Medium
- Low

### 4.2 Retrieval-Augmented Generation (RAG)

The RAG pipeline uses:

- SentenceTransformer embeddings.
- ChromaDB persistent vector storage.
- Cosine similarity search.
- Top-K document retrieval.
- Local Qwen LLM for response generation.

The knowledge base contains IT troubleshooting and support procedures.

### 4.3 Agentic AI with LangGraph

LangGraph orchestrates the IT support workflow using separate processing nodes:

- Input validation.
- Ticket classification.
- Knowledge retrieval.
- Output validation.
- Decision making.
- Employee response.
- Ticket escalation.
- IT action handling.

### 4.4 Dual Human Approval Workflow

Sensitive operations require two approvals.

**Workflow:**

Employee Request → Manager Approval → IT Approval → Simulated IT Action → Ticket Completed

Supported workflows:

- Software installation.
- Application access requests.

The system records approval decisions, approver information, timestamps, and action history.

### 4.5 Password Reset

The password-reset demonstration includes:

- Conditional password-reset form.
- New password and confirmation.
- PBKDF2-HMAC-SHA256 password hashing.
- Random salt generation.

This is a local demonstration and does not authenticate employees against a real corporate identity provider.

### 4.6 Security Guardrails

**Input guardrails:**

- Prompt injection detection.
- Credential theft phrase detection.
- Sensitive numeric information detection.
- Empty input validation.
- Maximum input length validation.

**Output guardrails:**

- Detect unsafe password and OTP requests.
- Block selected false IT action completion claims.
- Replace blocked responses with a safe fallback message.

### 4.7 Audit and Performance Monitoring

Performance metrics include:

- Retrieval latency.
- LLM response latency.
- Total processing time.
- Prompt token count.
- Completion token count.
- Model information.
- External API cost tracking.

Audit history records simulated IT action execution.

---

## 5. Project Structure

```text
TelecomCare-AI/
│
├── agents/
│   ├── __init__.py
│   ├── it_agent.py
│   └── test_agent.py
│
├── backend/
│   ├── __init__.py
│   ├── main.py
│   └── approval_api.py
│
├── frontend/
│   ├── app.py
│   ├── manager.py
│   └── admin.py
│
├── rag/
│   ├── __init__.py
│   ├── embeddings.py
│   ├── vector_store.py
│   ├── answer_generator.py
│   ├── test_rag.py
│   └── test_performance.py
│
├── guardrails/
│   ├── __init__.py
│   ├── input_guardrail.py
│   └── test_input_guardrail.py
│
├── database/
│   ├── __init__.py
│   └── db.py
│
├── tools/
│   ├── __init__.py
│   ├── action_executor.py
│   ├── human_approval.py
│   ├── it_tools.py
│   └── audit_logger.py
│
├── evaluation/
│   ├── __init__.py
│   ├── test_cases.json
│   └── evaluate_classifier.py
│
├── data/
│   ├── generate_data.py
│   ├── tickets.csv
│   └── knowledge_base.json
│
├── logs/
│   └── performance_logger.py
│
├── tests/
│   ├── test_action_executor.py
│   ├── test_human_approval.py
│   └── test_it_tools.py
│
├── docs/
│   ├── architecture.md
│   └── project_report.md
│
├── screenshots/
│   ├── 01_password_reset.png
│   ├── 02_software_installation_request.png
│   ├── 03_vpn_troubleshooting.png
│   ├── 04_manager_approval.png
│   ├── 05_it_approval.png
│   └── 06_completed_request.png
│
├── requirements.txt
├── README.md
└── .gitignore
```

**Note:** The SQLite database (`tickets.db`), ChromaDB storage (`database/chroma_db/`), and generated JSONL log files are created locally at runtime. They are excluded from the Git repository through `.gitignore`.

---

## 6. Installation and Setup

### Prerequisites

- Python 3.12
- Git
- Ollama
- VS Code (recommended)

### Step 1: Clone the repository

```bash
git clone https://github.com/komalnimjework/TelecomCare-AI.git
cd TelecomCare-AI
```

### Step 2: Create a virtual environment

```bash
python -m venv .venv
```

Activate on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Install and start Ollama

Install Ollama from:

https://ollama.com/

Download the required model:

```bash
ollama pull qwen2.5:1.5b
```

Verify the model:

```bash
ollama list
```

Ensure Ollama is running locally.

### Step 5: Start the FastAPI backend

```bash
python -m uvicorn backend.main:app --reload
```

API documentation:

http://127.0.0.1:8000/docs

### Step 6: Start the Employee Portal

Open another terminal:

```bash
python -m streamlit run frontend/app.py --server.port 8501
```

Employee Portal:

http://localhost:8501

### Step 7: Start the Manager Portal

Open another terminal:

```bash
python -m streamlit run frontend/manager.py --server.port 8502
```

Manager Portal:

http://localhost:8502

Demo Manager ID: `MGR001`

### Step 8: Start the IT Admin Portal

Open another terminal:

```bash
python -m streamlit run frontend/admin.py --server.port 8503
```

IT Admin Portal:

http://localhost:8503

Demo IT Approver ID: `IT001`

---

## 7. Testing and Evaluation

Run classification evaluation:

```bash
python -m evaluation.evaluate_classifier
```

Run RAG retrieval testing:

```bash
python -m rag.test_rag
```

The evaluation dataset contains 10 synthetic test cases.

### Initial Classification Evaluation Results

| Metric | Category | Priority |
|---|---:|---:|
| Accuracy | 100% | 100% |
| Precision | 100% | 100% |
| Recall | 100% | 100% |
| F1-score | 100% | 100% |

- Total test cases: 10
- Correct predictions: 10
- Incorrect predictions: 0

**Evaluation limitation:** These results represent the initial 10-case synthetic evaluation dataset. They should not be interpreted as production-level accuracy. Larger and more diverse validation datasets are required.

---

## 8. Cost Optimization

The system uses local inference to reduce external API expenses.

Cost optimization techniques:

- Local Ollama model inference.
- Local SentenceTransformer embeddings.
- Persistent ChromaDB storage.
- SQLite database.
- No paid external LLM API calls in the tested workflows.

External model API cost recorded in the performance logs: $0.

Local hardware, storage, and electricity costs still apply.

---

## 9. Important Implementation Limitations

This project is a functional local MVP and assignment demonstration.

- Software installation is simulated; no actual software is installed.
- Application access is simulated; no real permissions are changed.
- Password reset is a demonstration and does not integrate with corporate identity verification.
- Manager and IT approver IDs are demo identifiers, not production authentication.
- Guardrails use rule-based checks and are not comprehensive security controls.
- The evaluation dataset is small and synthetic.

Production deployment would require enterprise authentication, authorization, secure secrets management, comprehensive security testing, real ITSM integrations, and operational monitoring.

---

## 10. Future Enhancements

- Integrate ServiceNow or Jira Service Management.
- Add enterprise identity integration using OAuth2 or SSO.
- Improve RAG with hybrid retrieval and reranking.
- Expand the knowledge base.
- Add more comprehensive evaluation datasets.
- Introduce advanced guardrails and security testing.
- Add real-time IT infrastructure monitoring.
- Deploy using Docker and cloud infrastructure.

---

## 11. Project Outcome

TelecomCare AI demonstrates how Agentic AI, RAG, local LLM inference, and human approval workflows can be combined to automate common enterprise IT support processes.

The MVP demonstrates intelligent issue classification, knowledge-based troubleshooting, ticket management, dual approval, simulated action execution, security validation, and performance monitoring.

**Project:** TelecomCare AI  
**Category:** Agentic AI / Generative AI / IT Automation  
**Primary Framework:** LangGraph  
**LLM:** Qwen 2.5 1.5B  
**Vector Database:** ChromaDB  
**Backend:** FastAPI  
**Frontend:** Streamlit
