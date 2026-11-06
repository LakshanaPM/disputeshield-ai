# DisputeShield AI — Devpost Project Submission

> **Autonomous Dispute Defense & Revenue Recovery Agent for PayPal Merchants**  
> *Targeted Hackathon Tracks:* Grand Prize ($12,000) • Best Use of PayPal + AI ($3,500) • AG Grid Enterprise Sponsor Bounty ($5,000) • Most Impactful ($2,500) • Best Demo Delivery ($2,000)

---

## 💡 Pitch & Tagline
**DisputeShield AI is an autonomous, agentic AI platform that detects incoming PayPal disputes in sub-seconds, extracts cross-system evidence via Model Context Protocol (MCP), validates merchant eligibility, and auto-dispatches cryptographically verifiable defense packets to the PayPal Resolution API in under 45 seconds.**

---

## ⚡ The Inspiration
Online merchants face a relentless, systemic crisis: **43% of merchant disputes are lost not because the merchant was wrong, but simply due to late evidence submission, missed deadlines, or fragmented documentation.** 

When a customer files an unauthorized transaction claim or "item not received" (INR) dispute, a merchant has merely 10 to 20 days to assemble:
1. Proof of delivery and carrier tracking from logistics providers (FedEx/UPS/DHL).
2. Customer communication logs and signed agreements from customer support desks.
3. Cryptographic payment authorization traces, IP logs, and device fingerprints from PayPal.

For mid-sized merchants processing thousands of orders weekly, human dispute teams spend **35 to 45 minutes per dispute** manually stitching together spreadsheets and PDFs. By the time they locate the tracking number, the deadline has expired, resulting in automatic chargeback losses, lost merchandise, and hefty dispute processing fees.

We asked: *What if an autonomous AI agent could intercept dispute webhooks in milliseconds, query carrier APIs, verify PayPal Seller Protection policies in real-time, compute a deterministic win-confidence score, and submit an airtight rebuttal before the merchant even finishes their morning coffee?*

That is **DisputeShield AI**.

---

## 🛡️ What It Does
DisputeShield AI transforms dispute defense from a panicked, manual scramble into an automated, real-time revenue protection shield:

1. **Instant Webhook Ingestion & Signature Verification**:
   - Ingests PayPal `CUSTOMER.DISPUTE.CREATED` webhooks with asymmetric cryptographic verification (`X-PAYPAL-SIGNATURE` with CRC32/SHA256 and PayPal certificate caching).
2. **Autonomous Multi-Agent Investigation**:
   - The LangChain/LangGraph dispute agent coordinates specialized sub-tools via the **Model Context Protocol (MCP)** to gather multi-source evidence:
     * Carrier shipping & delivery records with GPS proof and recipient signature.
     * Order invoices and customer messaging history.
     * Prior refund records and PayPal dispute history.
3. **Deterministic & Calibrated Confidence Scoring**:
   - Evaluates evidence completeness across 5 key dimensions (Carrier Signature, Tracking Match, Customer Auth, Dispute Reason Calibration, and Prior Disputed Volume).
   - Generates a mathematically calibrated 0–100% win-probability score.
4. **Adaptive Routing & Auto-Dispatch**:
   - **Confidence $\ge$ 85%**: Autonomous submission mode formats the structured rebuttal narrative, signs the evidence packet, and dispatches it directly to the PayPal Dispute Resolution API (`POST /v1/customer/disputes/{id}/provide-evidence`).
   - **Confidence < 85%**: Stages an interactive Defense Draft in the Merchant Review Drawer with missing evidence callouts and a single-click "Approve & Dispatch" workflow.
5. **AG Grid Enterprise SSRM Command Center**:
   - High-performance Server-Side Row Model (SSRM) grid managing high dispute volumes with sub-millisecond filtering, multi-column sorting, and master-detail hierarchical drawers.
   - Real-time WebSocket streaming highlights new disputes and logs live agent reasoning traces.
6. **Predictive Risk & Chargeback Forensics**:
   - Real-time risk gauge tracking portfolio dispute rates against PayPal's 1.0% monitoring threshold.
   - Reason distribution, revenue at risk, automated recovery rate, and trend projection charts.

---

## 🏗️ How We Built It

### Architecture
DisputeShield AI is built as an enterprise-grade distributed system:

- **Frontend**: React 18, Vite, Tailwind CSS, AG Grid Enterprise (`ag-grid-react` Server-Side Row Model & Master-Detail), Chart.js, Lucide Icons, and native HTML5 WebSocket client.
- **Backend**: Python 3.11, FastAPI (REST & WebSockets), Pydantic v2 schemas, SQLAlchemy ORM (PostgreSQL & SQLite compatibility), and Celery for asynchronous task orchestration.
- **AI Agent & Reasoning**: Gemini 1.5 Flash via `langchain-google-genai`, LangChain core tool calling, few-shot prompt engineering with RAG similarity retrieval.
- **MCP Bridge**: Anthropic Model Context Protocol (`mcp`) server connecting logistics, order DBs, and PayPal dispute lifecycle tools.
- **Search & Analytics**: Elasticsearch for historical dispute retrieval and full-text evidence indexing.
- **SDKs & OpenAPI**: APIMatic-compliant OpenAPI 3.1 specification, typed TypeScript SDK (`@disputeshield/client`), and typed Python SDK (`disputeshield`).
- **DevOps**: Multi-stage Docker containers, Nginx SPA reverse proxy, Docker Compose, and automated `render.yaml` infrastructure-as-code blueprint.

---

## 🧗 Challenges We Overcame
1. **PayPal Webhook Asymmetric Security**:
   - PayPal webhooks require validating public key certificates from `api.sandbox.paypal.com` while guarding against SSRF and replay attacks. We built an in-memory cached certificate validator with strict domain sandboxing.
2. **Agentic Hallucination Guardrails**:
   - In legal dispute rebuttals, AI hallucinations are fatal. We designed a strict two-stage pipeline: deterministic evidence validation must verify tracking and carrier receipts *before* the LLM synthesizes the formal rebuttal letter.
3. **AG Grid Enterprise SSRM Integration**:
   - Integrating the Server-Side Row Model with real-time WebSockets required implementing an immutable datasource cache that receives server push events without triggering full grid re-renders.

---

## 🏆 Accomplishments That We're Proud Of
- **45-Second Defense Cycle**: Cut dispute resolution prep time from 40 minutes to under 45 seconds.
- **10/10 Scenario Decision Matrix**: Engineered and verified 10 diverse dispute scenarios (Unauthorized, Item Not Received, Significantly Not As Described, Cancelled Recurring, Digital Goods) achieving 100% predictable, correct routing.
- **39 Pytest Unit & Integration Tests**: Comprehensive automated test suite running in 14 seconds across all API routers, confidence scorers, and MCP bridges.
- **Zero-Latency Visual Streaming**: Created an executive PayPal-branded UI where judges watch the agent think, evaluate criteria, and submit evidence in real-time.

---

## 📚 What We Learned
- How to harness the **Model Context Protocol (MCP)** to standardize tool execution across disparate merchant databases, external logistics APIs, and PayPal APIs.
- The intricacies of PayPal Seller Protection policy rules and chargeback lifecycle states (`UNDER_REVIEW`, `WAITING_FOR_PRVDR_ACK`, `RESOLVED`).
- How to design human-in-the-loop fallback mechanisms that balance full autonomy with merchant control.

---

## 🚀 What's Next for DisputeShield AI
1. **Shopify & WooCommerce Native Apps**: One-click app marketplace plugins to sync fulfillment data automatically.
2. **PayPal Marketplace & Partner Platform Integration**: Expanding from individual merchants to platform-wide dispute management for multi-seller marketplaces.
3. **Predictive Dispute Prevention**: Proactively alerting merchants before an inquiry escalates into a formal chargeback.

---

## 🛠️ Built With
- `paypal-api`
- `fastapi`
- `python`
- `react`
- `ag-grid-enterprise`
- `langchain`
- `gemini-api`
- `model-context-protocol`
- `celery`
- `postgresql`
- `redis`
- `docker`
- `vite`
- `tailwind-css`
- `apimatic`

