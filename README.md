# 🛡️ DisputeShield AI

> **Autonomous Agentic Dispute Defense for PayPal Merchants**  
> Official Submission for the **PayPal AI Hackathon 2026** (Grand Prize Target, Best Use of PayPal + AI, AG Grid Enterprise Sponsor Bounty).

[![Live Demo](https://img.shields.io/badge/Demo-Live_Web_App-0079C1?style=for-the-badge&logo=render)](https://disputeshield-frontend-gt1j.onrender.com)
[![Video Demo](https://img.shields.io/badge/YouTube-Video_Walkthrough-FF0000?style=for-the-badge&logo=youtube)](https://youtu.be/YR1iVlWnZdc)
[![API Docs](https://img.shields.io/badge/FastAPI-Swagger_Docs-009688?style=for-the-badge&logo=fastapi)](https://disputeshield-api-1p7w.onrender.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)

DisputeShield AI is a proactive, agentic defense platform designed to protect high-volume PayPal merchants against chargebacks, Item Not Received (INR), and Significantly Not As Described (SNAD) disputes. Powered by **Model Context Protocol (MCP)**, **LangChain agentic reasoning**, **Elasticsearch vector RAG**, and an **AG Grid Enterprise Server-Side Row Model (SSRM)** command center, DisputeShield automates counter-evidence assembly, calculates empirical confidence, and enforces strict risk guardrails.

---

## ⚡ Key Highlights & Architecture

- **Autonomous Webhook Ingestion**: Receives PayPal `CUSTOMER.DISPUTE.*` webhooks, parses transaction and dispute metadata, and schedules autonomous background tasks within sub-200ms.
- **MCP & Tool-Calling Pipeline**: Direct integration with the `@paypal/mcp` stdio server, complemented by resilient asynchronous fallback wrappers (`PayPalClient`, `ElasticsearchService`).
- **LangChain & AI Triage Agent**: Evaluates claim urgency, response deadlines, and dispute categories (INR, SNAD, Unauthorized). Dynamically inspects orders and carrier tracking via registered tools before synthesizing seller explanations.
- **RAG Precedent Retrieval**: Queries dense 1536-dimensional vector embeddings and empirical precedent win rates in Elasticsearch to optimize defense arguments.
- **Calibrated Confidence Scoring**: 
  - `≥ 80% Confidence`: **AUTO_SUBMIT** evidence to PayPal Sandbox without human intervention.
  - `60% – 79% Confidence`: **DRAFT_PENDING_REVIEW** with one-click merchant approval.
  - `< 60% Confidence`: **ESCALATE_TO_HUMAN** with full gap analysis.
- **AG Grid Enterprise Command Center**: Enterprise Server-Side Row Model (SSRM) with dynamic sorting, filtering, infinite scrolling, sparklines, and Master-Detail panels for deep-dive dispute inspection.

```mermaid
sequenceDiagram
    autonumber
    actor Buyer
    participant PayPal as PayPal API / Sandbox
    participant WH as FastAPI Webhook Receiver
    participant Task as Celery Worker / Processor
    participant Agent as DisputeShield AI Agent
    participant MCP as @paypal/mcp & PayPal Client
    participant ES as Elasticsearch (Vector RAG)
    participant DB as PostgreSQL / SQLite
    participant WS as WebSocket Hub
    participant UI as AG Grid Enterprise UI

    Buyer->>PayPal: File Dispute Claim
    PayPal->>WH: POST /api/webhooks/paypal
    WH->>DB: Store Raw Webhook Event
    WH->>Task: Enqueue process_dispute_webhook()
    WH-->>PayPal: 200 OK (< 200ms)
    Task->>MCP: Query Order, Tracking, & Customer Telemetry
    Task->>ES: Vector kNN Search (Similar Precedent Cases)
    ES-->>Task: 1536-dim Matched Precedents & Win Rate
    Task->>Agent: Triage & Evidence Synthesis (INR/SNAD/UNAUTH)
    Agent-->>Task: Compiled Counter-Evidence Package
    Task->>Task: Confidence Score Calculation (0-100%)
    alt Confidence >= 80% (Auto-Submit)
        Task->>MCP: Submit Counter-Evidence to PayPal
        Task->>DB: Record Outcome & Submitted Evidence
    else Confidence 60-79% (Draft)
        Task->>DB: Save Evidence Package (Pending Approval)
    else Confidence < 60% (Escalate)
        Task->>DB: Flag for Manual Review & Gap Resolution
    end
    Task->>WS: Broadcast Real-Time Agent Decision
    WS->>UI: Live Stream Event & Update AG Grid SSRM
```

---

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| **Backend & APIs** | FastAPI, Python 3.12, SQLAlchemy 2.0, Pydantic V2, Uvicorn |
| **Agentic AI & RAG** | LangChain Core, OpenAI GPT-4o, Google Gemini 2.0 Flash, Model Context Protocol (`@paypal/mcp`) |
| **Search & Precedents** | Elasticsearch 8.15 (1536-dim dense vectors, kNN similarity) |
| **Databases & Queues** | PostgreSQL 16, Redis 7, Celery 5.4, SQLite (local dev fallback) |
| **Frontend & Grid** | React 18, Vite, AG Grid Enterprise 36.2 (SSRM, Master-Detail, Sparklines), Recharts, Tailwind CSS |
| **Integration & Tools** | APIMatic (OpenAPI 3.1 SDK ready), Docker Compose, Render Blueprint |

---

## 🚀 Quickstart Guide

### Option 1: Docker Compose (Recommended)

Run the complete multi-service stack with a single command:

```bash
# Clone the repository
git clone https://github.com/LakshanaPM/disputeshield-ai.git
cd disputeshield-ai

# Copy environment template
cp .env.example .env

# Launch PostgreSQL, Redis, Elasticsearch, and FastAPI Backend
docker compose up -d

# Verify services
docker compose ps
```

The FastAPI application will be available at `http://localhost:8000` (`/docs` for interactive Swagger UI).

### Option 2: Manual Local Development

#### 1. Backend Setup
```bash
cd backend
python -m venv venv
# Windows:
.\venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Access the client dashboard at `http://localhost:5173`.

---

## ⚙️ Environment Configuration

Copy `.env.example` to `.env` and configure your credentials:

```ini
# PayPal Sandbox API
PAYPAL_CLIENT_ID=your_sandbox_client_id
PAYPAL_CLIENT_SECRET=your_sandbox_client_secret
PAYPAL_ENVIRONMENT=SANDBOX
PAYPAL_WEBHOOK_ID=your_sandbox_webhook_id
PAYPAL_BASE_URL=https://api-m.sandbox.paypal.com

# LLM Providers
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4o
GEMINI_API_KEY=your_gemini_api_key

# Database & Search Infrastructure
DATABASE_URL=postgresql://disputeshield:disputeshield@localhost:5432/disputeshield
ELASTICSEARCH_URL=http://localhost:9200
REDIS_URL=redis://localhost:6379/0

# AG Grid Enterprise
VITE_AG_GRID_LICENSE_KEY=your_ag_grid_enterprise_license_key
```

---

## 📦 Key PayPal Domains & AG Grid Enterprise Features

### PayPal API Integration Surface
- **Disputes API (`/v1/customer/disputes`)**: Ingests claims, fetches timeline histories, submits counter-evidence payloads, accepts claims, and executes appeals.
- **Orders API (`/v2/checkout/orders`)**: Fetches item descriptions, billing units, and verified recipient addresses.
- **Shipment Trackers API (`/v1/shipping/trackers`)**: Validates carrier status, delivery timestamps, GPS matches, and recipient signature images.
- **Invoicing API (`/v2/invoicing/invoices`)**: Retrieves digital service receipts and license verification records.
- **Model Context Protocol (`@paypal/mcp`)**: Native tool provider for agentic tool loops and automated resolution.

### AG Grid Enterprise Capabilities
- **Server-Side Row Model (SSRM)**: Infinite scrolling and on-demand pagination against `/api/disputes`.
- **Master-Detail Row Expansion**: Interactive detail views rendering order breakdowns, carrier portals, editable counter-defense statements, and RAG precedent matches.
- **Sparklines & Mini Gauges**: In-grid visualization of rolling dispute frequency and real-time confidence scores.
- **Custom React Cell Renderers**: Dynamic status pills, carrier badges, and relative date formatters.

---

## 🧪 Testing & Verification

Execute the complete test suite across agent triage, RAG retrieval, MCP bridging, and API endpoints:

```bash
# 1. Run all backend tests
pytest backend/tests/ -v

# 2. Run the 10-scenario decision matrix harness
python backend/tests/test_scenario_matrix.py

# 3. Compile frontend bundle
cd frontend && npm run build
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

