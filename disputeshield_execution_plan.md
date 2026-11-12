# 🗺️ DisputeShield AI — Execution Plan

> **Objective:** Build, deploy, and submit DisputeShield AI to win the PayPal AI Hackathon Grand Prize ($12K) + AG Grid Sponsor Prize ($5K)
> **Timeline:** Oct 18 → Nov 12, 2026 (25 days)
> **Status:** Ready to Execute

---

## 📐 Architecture Decisions (Locked In)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Backend framework** | FastAPI (Python 3.12) | Async-native, excellent for webhooks + background tasks; LangChain ecosystem is Python-first |
| **AI framework** | LangChain + OpenAI GPT-4o | Best tool-calling support; native MCP integration path; most mature agent framework |
| **PayPal integration** | `@paypal/mcp` server + direct REST fallback | MCP = strategic alignment with PayPal's vision; REST fallback for endpoints not yet in MCP |
| **Database** | PostgreSQL 16 | Transactional data (disputes, merchants, evidence); reliable; Render-native |
| **Search & RAG** | Elasticsearch 8.x | Vector search for RAG; full-text search for dispute history; ES|QL for analytics; Elastic sponsor alignment |
| **Frontend framework** | React 18 + Vite | Fast dev server; industry standard; AG Grid has first-class React wrapper |
| **Data grid** | AG Grid Enterprise (trial) | Sponsor prize target; sparklines, SSRM, master-detail are Enterprise features |
| **Charts** | Recharts | Lightweight, React-native, beautiful defaults |
| **Styling** | Vanilla CSS (custom design system) | Full control over glassmorphism + dark mode; no framework bloat |
| **Real-time updates** | WebSocket (FastAPI WebSocket) | Live dashboard updates when agent processes disputes |
| **Task queue** | Celery + Redis | Background processing of webhook events; agent runs async |
| **Deployment** | Render (Web Service + Worker + PostgreSQL) | Sponsor alignment; simple deployment; free tier available |
| **Containerization** | Docker Compose (local dev) | Judges can `docker compose up` to run everything |

---

## 📁 Project Structure

```
disputeshield-ai/
├── README.md                          # Setup instructions, architecture, screenshots
├── LICENSE                            # MIT License
├── .env.example                       # All required environment variables
├── docker-compose.yml                 # Local dev: FastAPI + PostgreSQL + Elasticsearch + Redis
├── render.yaml                        # Render deployment blueprint
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                        # FastAPI app entry point
│   ├── config.py                      # Settings from env vars (Pydantic BaseSettings)
│   ├── database.py                    # SQLAlchemy engine + session
│   ├── models/
│   │   ├── __init__.py
│   │   ├── dispute.py                 # Dispute ORM model
│   │   ├── evidence.py                # Evidence ORM model
│   │   ├── merchant.py                # Merchant ORM model
│   │   └── webhook_event.py           # Raw webhook event log
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── dispute.py                 # Pydantic request/response schemas
│   │   ├── evidence.py
│   │   └── webhook.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── webhooks.py                # POST /webhooks/paypal — webhook receiver
│   │   ├── disputes.py                # GET/POST /api/disputes — dashboard CRUD
│   │   ├── analytics.py               # GET /api/analytics — risk dashboard data
│   │   └── ws.py                      # WebSocket endpoint for real-time updates
│   ├── services/
│   │   ├── __init__.py
│   │   ├── paypal_client.py           # PayPal REST API client (Orders, Disputes, Tracking)
│   │   ├── webhook_verifier.py        # PayPal webhook signature verification
│   │   ├── mcp_bridge.py              # Bridge between LangChain agent and @paypal/mcp
│   │   └── elasticsearch_service.py   # ES indexing, vector search, ES|QL queries
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── dispute_agent.py           # Main LangChain agent — triage + evidence + submit
│   │   ├── tools.py                   # Custom LangChain tools wrapping MCP/PayPal calls
│   │   ├── evidence_engine.py         # Evidence compilation logic per dispute type
│   │   ├── rag_retriever.py           # Elasticsearch vector retrieval for similar cases
│   │   ├── confidence_scorer.py       # Confidence calculation + auto/draft/escalate decision
│   │   └── prompts.py                 # System prompts and prompt templates
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── celery_app.py              # Celery configuration
│   │   └── dispute_processor.py       # Celery task: process webhook → run agent
│   └── tests/
│       ├── test_webhook_receiver.py
│       ├── test_dispute_agent.py
│       └── test_evidence_engine.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── public/
│   │   └── favicon.svg
│   ├── src/
│   │   ├── main.jsx                   # React entry point
│   │   ├── App.jsx                    # Root component + router
│   │   ├── index.css                  # Global design system (CSS variables, fonts, base)
│   │   ├── api/
│   │   │   ├── client.js              # Axios instance with base URL
│   │   │   ├── disputes.js            # Dispute API calls
│   │   │   └── analytics.js           # Analytics API calls
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js        # WebSocket hook for real-time updates
│   │   │   └── useDisputeData.js      # Data fetching + caching hook
│   │   ├── components/
│   │   │   ├── Layout/
│   │   │   │   ├── TopNav.jsx         # Navigation bar with logo + notifications
│   │   │   │   ├── Sidebar.jsx        # Agent activity panel
│   │   │   │   └── Layout.jsx         # Main layout wrapper
│   │   │   ├── Dashboard/
│   │   │   │   ├── StatCards.jsx       # Animated stat cards row
│   │   │   │   ├── DisputeGrid.jsx    # AG Grid dispute queue (main component)
│   │   │   │   ├── DisputeDetail.jsx  # Master-detail expanded row
│   │   │   │   └── DisputeTimeline.jsx# Vertical timeline for dispute lifecycle
│   │   │   ├── RiskDashboard/
│   │   │   │   ├── RiskGauge.jsx      # Account health gauge
│   │   │   │   ├── TrendChart.jsx     # Dispute ratio trend (Recharts)
│   │   │   │   └── AlertPanel.jsx     # Predictive risk alerts
│   │   │   ├── Agent/
│   │   │   │   ├── AgentLog.jsx       # Live reasoning trace
│   │   │   │   ├── ConfidenceGauge.jsx# Circular confidence indicator
│   │   │   │   └── EvidenceChecklist.jsx # Evidence items with status
│   │   │   └── common/
│   │   │       ├── Badge.jsx          # Color-coded status badges
│   │   │       ├── AnimatedCounter.jsx# Count-up animation
│   │   │       ├── GlassCard.jsx      # Glassmorphism container
│   │   │       └── LoadingPulse.jsx   # Pulsing loading indicator
│   │   └── utils/
│   │       ├── formatters.js          # Currency, date, percentage formatters
│   │       └── constants.js           # Dispute types, status enums, colors
│   └── ag-grid-theme.css              # Custom AG Grid dark theme
│
├── mcp/
│   ├── package.json                   # @paypal/mcp dependency
│   └── start.sh                       # Script to start MCP server with sandbox creds
│
└── scripts/
    ├── seed_disputes.py               # Seed sandbox with sample disputes for demo
    ├── simulate_webhook.py            # Fire a test webhook locally
    └── generate_demo_data.py          # Generate realistic dispute history for RAG
```

---

## 🔨 Phase 1: Foundation & Core Pipeline (Days 1–7)

### Day 1 (Oct 18) — Project Scaffold & Environment

**Tasks:**
1. Create project directory with full folder structure above
2. Initialize FastAPI backend with `requirements.txt`
3. Initialize React frontend with Vite (`npx -y create-vite@latest ./`)
4. Write `docker-compose.yml` (FastAPI + PostgreSQL + Elasticsearch + Redis)
5. Create `.env.example` with all variables
6. Create `config.py` with Pydantic BaseSettings
7. Set up basic FastAPI app with health check endpoint
8. Set up basic React app with design system CSS

**Key Dependencies (backend/requirements.txt):**
```
fastapi==0.115.*
uvicorn[standard]==0.30.*
sqlalchemy==2.0.*
alembic==1.13.*
psycopg2-binary==2.9.*
celery[redis]==5.4.*
langchain==0.3.*
langchain-openai==0.2.*
openai==1.50.*
elasticsearch==8.15.*
httpx==0.27.*
pydantic-settings==2.5.*
python-multipart==0.0.9
websockets==13.*
```

**Key Dependencies (frontend/package.json):**
```
react, react-dom, react-router-dom,
ag-grid-react, ag-grid-enterprise,
recharts, axios
```

**Success Criteria:** `docker compose up` starts all services; FastAPI returns `{"status": "ok"}` on `/health`; React dev server shows the app shell.

---

### Day 2 (Oct 19) — PayPal Sandbox & Database Models

**Tasks:**
1. Create PayPal Developer Sandbox application at [developer.paypal.com](https://developer.paypal.com)
2. Generate sandbox REST API credentials (Client ID + Secret)
3. Create sandbox buyer + seller test accounts
4. Write `paypal_client.py` — token generation, base request method
5. Test: call `GET /v1/customer/disputes` against sandbox
6. Write SQLAlchemy ORM models:
   - `Dispute` (id, paypal_dispute_id, reason, status, amount, currency, created_at, updated_at, evidence_status, confidence_score, agent_decision, resolution)
   - `Evidence` (id, dispute_id, type, content, file_url, submitted_at, status)
   - `Merchant` (id, paypal_merchant_id, name, dispute_ratio, account_health_score)
   - `WebhookEvent` (id, event_id, event_type, payload_json, processed, created_at)
7. Run Alembic migration to create tables

**Success Criteria:** Can authenticate with PayPal Sandbox and list disputes; database tables created and accessible.

---

### Day 3 (Oct 20) — Webhook Receiver

**Tasks:**
1. Write `webhook_verifier.py` — implement PayPal webhook signature verification:
   - Fetch PayPal's signing certificate from `cert_url`
   - Verify transmission signature using `transmission_id`, `transmission_time`, `webhook_id`, `event_body`
2. Write `api/webhooks.py`:
   - `POST /webhooks/paypal` endpoint
   - Verify signature → store raw event → enqueue Celery task → return 200
   - Idempotency check: skip if `event_id` already processed
3. Write `simulate_webhook.py` script to fire test webhooks locally
4. Set up Celery + Redis:
   - `celery_app.py` configuration
   - `dispute_processor.py` — skeleton task that logs received events
5. Register PayPal webhook URL in sandbox dashboard (or use ngrok for local testing)

**Success Criteria:** Simulated webhook is received, verified, stored in DB, and enqueued as Celery task.

---

### Day 4 (Oct 21) — Disputes API Full Integration

**Tasks:**
1. Implement in `paypal_client.py`:
   - `list_disputes(status, start_time, end_time)` → `GET /v1/customer/disputes`
   - `get_dispute_details(dispute_id)` → `GET /v1/customer/disputes/{id}`
   - `provide_evidence(dispute_id, evidence_payload)` → `POST .../provide-evidence`
   - `accept_claim(dispute_id, note)` → `POST .../accept-claim`
   - `appeal_dispute(dispute_id, evidence_payload)` → `POST .../appeal`
2. Create sandbox test disputes (use sandbox buyer account to create INR/SNAD disputes)
3. Write `api/disputes.py`:
   - `GET /api/disputes` — list from DB with filters, pagination, sorting (for AG Grid SSRM)
   - `GET /api/disputes/{id}` — detail view
   - `POST /api/disputes/{id}/approve` — merchant approves agent's draft
4. Test all 5 Disputes API endpoints against sandbox

**Success Criteria:** All 5 dispute endpoints work against sandbox; dashboard API returns dispute data with pagination.

---

### Day 5 (Oct 22) — Orders & Shipment Tracking APIs

**Tasks:**
1. Implement in `paypal_client.py`:
   - `get_order(order_id)` → `GET /v2/checkout/orders/{id}`
   - `get_tracking(tracking_number, carrier)` → `GET /v1/shipping/trackers/{id}`
2. Create sandbox test orders with tracking info
3. Build the evidence chain: dispute → linked order → shipment tracking → delivery confirmation
4. Write helper function: `build_evidence_chain(dispute_id)` that fetches all related data

**Success Criteria:** Given a dispute ID, can retrieve the full chain: dispute details → order context → shipment tracking → delivery status.

---

### Day 6 (Oct 23) — Invoicing API & Complete Data Model

**Tasks:**
1. Implement in `paypal_client.py`:
   - `get_invoice(invoice_id)` → `GET /v2/invoicing/invoices/{id}`
   - `list_invoices(filters)` → `GET /v2/invoicing/invoices`
2. Create sandbox test invoices for digital goods scenarios
3. Complete the database schema — ensure all relationships are correct
4. Write `elasticsearch_service.py`:
   - Index creation with proper mappings (dispute text fields + dense_vector for embeddings)
   - `index_dispute(dispute_data)` — index a dispute document
   - `search_disputes(query, filters)` — full-text search
   - `vector_search(embedding, k)` — kNN search for similar disputes
5. Seed Elasticsearch with sample dispute data

**Success Criteria:** Invoicing API works; Elasticsearch is running with dispute index; can index and retrieve disputes.

---

### Day 7 (Oct 24) — MCP Server Integration

**Tasks:**
1. Set up `@paypal/mcp` in `mcp/` directory:
   - `npm init -y && npm install @paypal/mcp`
   - Configure `start.sh` with sandbox credentials
   - Test: `npx @paypal/mcp --tools=all` starts successfully
2. Write `mcp_bridge.py`:
   - Spawn MCP server as subprocess (or connect via stdio)
   - Implement LangChain `Tool` wrappers for each MCP capability
   - Map MCP tools to LangChain tool definitions with descriptions
3. Verify: LangChain agent can call `get_dispute_details` through MCP bridge
4. Document which PayPal operations go through MCP vs direct REST (fallback for any gaps)

**Success Criteria:** LangChain agent can successfully call PayPal operations through `@paypal/mcp` tool-calling; all tools are properly typed and described.

---

## 🤖 Phase 2: AI Agent & Evidence Engine (Days 8–14)

### Day 8 (Oct 25) — Agent Triage Logic

**Tasks:**
1. Write `agent/prompts.py`:
   - System prompt defining the agent's role, capabilities, and constraints
   - Triage prompt template: "Given this dispute, classify type, assess severity, recommend strategy"
2. Write `agent/dispute_agent.py`:
   - Initialize LangChain `AgentExecutor` with GPT-4o
   - Bind MCP tools (from Day 7)
   - Implement triage step: dispute type classification (INR / SNAD / Unauthorized / Other)
   - Severity scoring: amount × dispute history × merchant category risk
3. Test triage on 5 different dispute scenarios

**Success Criteria:** Agent correctly classifies dispute types and assigns severity scores for INR, SNAD, and Unauthorized scenarios.

---

### Day 9 (Oct 26) — Evidence Strategy Engine

**Tasks:**
1. Write `agent/evidence_engine.py`:
   - Evidence type mapping per dispute reason:
     - **INR (Item Not Received):** carrier tracking, delivery confirmation, shipping label, proof of delivery signature
     - **SNAD (Significantly Not As Described):** product description, photos, return policy, customer communications
     - **Unauthorized Transaction:** transaction auth proof, device/IP data, customer verification records
   - Evidence strength scoring: each piece of evidence rated 1-10 for relevance
   - Gap identification: "Missing tracking info — evidence strength only 4/10"
2. Test: given dispute type + available data, engine recommends optimal evidence package

**Success Criteria:** Evidence engine produces ranked evidence strategies for each dispute type with strength scores.

---

### Day 10 (Oct 27) — Evidence Compilation

**Tasks:**
1. Implement `compile_evidence(dispute_id, strategy)` in `evidence_engine.py`:
   - Fetch data from PayPal APIs (order, tracking, invoice) based on strategy
   - Format into PayPal Disputes API `provide-evidence` payload structure
   - Include: `evidence_type`, `evidence_info`, `documents`, `notes`
2. Generate natural-language merchant notes (agent writes the "seller's explanation")
3. Mock fulfillment database with realistic data (tracking numbers, delivery dates, product descriptions)
4. Test: evidence compilation produces valid API payload for INR and SNAD

**Success Criteria:** Agent compiles a valid, submission-ready evidence payload from PayPal API data + merchant context.

---

### Day 11 (Oct 28) — End-to-End Agent Pipeline

**Tasks:**
1. Wire the full pipeline in `dispute_processor.py` (Celery task):
   ```
   webhook received → parse event → fetch dispute details (MCP)
   → triage (agent) → build evidence strategy → compile evidence
   → submit evidence (MCP) → update DB → index in ES → notify via WebSocket
   ```
2. Test full pipeline: fire simulated `CUSTOMER.DISPUTE.CREATED` webhook → agent auto-responds
3. Add comprehensive error handling at each pipeline stage
4. Add logging: every agent step logged with timestamp, action, result
5. Test with 3 different dispute scenarios end-to-end

**Success Criteria:** Full unattended pipeline: simulated webhook → agent processes → evidence submitted → DB updated. Works for INR with tracking.

---

### Day 12 (Oct 29) — RAG Pipeline

**Tasks:**
1. Write `agent/rag_retriever.py`:
   - Generate embeddings for dispute descriptions using `text-embedding-3-small`
   - Store in Elasticsearch dense_vector field
   - Implement `retrieve_similar_cases(dispute_text, k=5)`:
     - Embed query → kNN search → return top-k with metadata (outcome, evidence used, response time)
2. Write `scripts/generate_demo_data.py`:
   - Generate 100+ realistic past disputes with varied types, outcomes, evidence strategies
   - Index all into Elasticsearch with embeddings
3. Integrate RAG into agent pipeline:
   - Before composing evidence, agent queries similar cases
   - Agent incorporates precedent into its reasoning: "4/5 similar cases won with tracking proof"
4. Test: RAG retrieval returns relevant similar disputes

**Success Criteria:** Agent queries Elasticsearch for similar past disputes and uses precedent to inform evidence strategy.

---

### Day 13 (Oct 30) — Confidence Scoring & Human-in-the-Loop

**Tasks:**
1. Write `agent/confidence_scorer.py`:
   - Inputs: evidence strength score, similar case win rate, dispute amount, merchant history
   - Output: 0-100 confidence score
   - Decision gates:
     - **≥ 80%:** Auto-submit evidence (no human needed)
     - **60-79%:** Draft evidence + notify merchant for review
     - **< 60%:** Escalate to merchant with full analysis, no draft
2. Implement notification system:
   - WebSocket message to frontend: `{type: "agent_decision", dispute_id, confidence, action, evidence_draft}`
   - `POST /api/disputes/{id}/approve` — merchant approves agent's draft
   - `POST /api/disputes/{id}/override` — merchant modifies evidence before submission
3. Test all three confidence paths with different scenarios

**Success Criteria:** High-confidence disputes auto-submit; low-confidence disputes wait for merchant approval; merchant can approve/modify via API.

---

### Day 14 (Oct 31) — Risk Prediction Module

**Tasks:**
1. Implement in `services/risk_predictor.py`:
   - Calculate current dispute ratio (disputes / transactions in rolling 90-day window)
   - Trend analysis: is the ratio increasing, stable, or decreasing?
   - Threshold alerts:
     - **Green (< 0.5%):** Healthy
     - **Yellow (0.5-1.0%):** Watch
     - **Orange (1.0-1.5%):** Warning — recommend proactive measures
     - **Red (> 1.5%):** Critical — account limitation risk
   - Proactive recommendations: "Consider adding tracking to all orders over $50"
2. Write `api/analytics.py`:
   - `GET /api/analytics/risk-score` — current risk metrics
   - `GET /api/analytics/dispute-trends` — time-series data for charts
   - `GET /api/analytics/win-rate` — dispute outcome statistics
3. Seed realistic analytics data for demo

**Success Criteria:** Risk API returns meaningful metrics; trend analysis identifies rising dispute ratios; threshold alerts fire correctly.

---

## 🎨 Phase 3: Frontend & Polish (Days 15–21)

### Day 15 (Nov 1) — Design System & Layout Shell

**Tasks:**
1. Implement `index.css` — complete design system:
   - CSS custom properties (all colors, spacing, typography, shadows, transitions)
   - Dark mode as default
   - Glassmorphism utility classes (`.glass-card`, `.glass-panel`)
   - Animation keyframes (fadeIn, slideInRight, pulseGlow, countUp)
   - Google Fonts: Inter (400, 500, 600, 700)
2. Build layout components:
   - `Layout.jsx` — main grid layout (nav + sidebar + content)
   - `TopNav.jsx` — logo, notification bell (animated badge), account health pill
   - `Sidebar.jsx` — agent activity log container
3. Build common components:
   - `GlassCard.jsx` — glassmorphism container with border glow
   - `Badge.jsx` — status badges (Won/Lost/Pending/In Progress)
   - `AnimatedCounter.jsx` — count-up animation on mount
   - `LoadingPulse.jsx` — pulsing skeleton loader

**Success Criteria:** App shell renders with dark mode, glassmorphism panels, proper typography, and layout grid. Looks premium even without data.

---

### Day 16 (Nov 2) — AG Grid Dispute Queue

**Tasks:**
1. Install and configure AG Grid Enterprise (trial license)
2. Create custom AG Grid dark theme (`ag-grid-theme.css`) matching design system
3. Build `DisputeGrid.jsx`:
   - **Server-Side Row Model:** Fetches from `GET /api/disputes` with pagination, sorting, filtering
   - **Columns:**
     - Dispute ID (linked)
     - Type (INR/SNAD/Unauthorized) — custom badge renderer
     - Amount — currency formatter with trend arrow
     - Status — custom pill renderer with color coding
     - Evidence Status — icon + progress bar renderer
     - Confidence Score — mini circular gauge renderer
     - Trend — AG Grid sparkline (dispute frequency over time)
     - Created Date — relative time formatter
   - **Row Grouping:** Group by dispute type or status
   - **Quick Filter:** Global search across all columns
   - **Column Menu:** Preset views (All, Active, Won, Lost)
4. Build `DisputeDetail.jsx` — master-detail panel:
   - Dispute timeline
   - Evidence items with status
   - Agent reasoning trace
   - Action buttons (Approve / Modify / Escalate)

**Success Criteria:** AG Grid renders with all advanced features; data loads from API with SSRM; custom renderers look premium; master-detail expands.

---

### Day 17 (Nov 3) — Stat Cards & Real-Time Updates

**Tasks:**
1. Build `StatCards.jsx`:
   - **Total Disputes** — animated counter with trend badge
   - **Win Rate** — circular progress ring (animated fill)
   - **Avg Response Time** — gauge with "minutes" unit
   - **Money Saved** — currency counter with sparkline
   - All cards use glassmorphism styling
2. Implement `useWebSocket.js` hook:
   - Connect to `ws://backend/ws/disputes`
   - Handle message types: `new_dispute`, `agent_update`, `evidence_submitted`, `dispute_resolved`
   - Trigger UI updates: new row in grid, stat card animations, notification toast
3. Build notification toast system:
   - Slide-in from top-right
   - Color-coded by type (new dispute = warning, evidence submitted = success)
   - Auto-dismiss after 5 seconds

**Success Criteria:** Stat cards animate on load; WebSocket delivers real-time updates; new disputes trigger visible UI reaction.

---

### Day 18 (Nov 4) — Agent Activity Panel

**Tasks:**
1. Build `AgentLog.jsx`:
   - Real-time stream of agent actions (received via WebSocket)
   - Each entry: timestamp, action icon, description, status
   - Entries animate in (slide + fade)
   - Color-coded: analyzing = blue, fetching = yellow, submitting = green, escalating = orange
2. Build `ConfidenceGauge.jsx`:
   - Circular SVG gauge (0-100%)
   - Color gradient: red → yellow → green
   - Animated fill on update
   - Label: "AUTO-SUBMIT" / "NEEDS REVIEW" / "ESCALATED"
3. Build `EvidenceChecklist.jsx`:
   - List of evidence items with checkmark/pending/missing icons
   - Evidence type label + source (e.g., "Tracking: USPS 9400111..." )
   - Strength score bar

**Success Criteria:** Agent panel shows live reasoning trace during dispute processing; confidence gauge updates dynamically; evidence checklist reflects actual agent actions.

---

### Day 19 (Nov 5) — Risk Dashboard

**Tasks:**
1. Build `RiskGauge.jsx`:
   - Large semicircular gauge showing account health score (0-100)
   - Color zones: green / yellow / orange / red
   - Current dispute ratio displayed numerically below
2. Build `TrendChart.jsx` (Recharts):
   - Line chart: dispute count over time (30/60/90 day views)
   - Area chart: dispute ratio trend with danger threshold line
   - Bar chart: disputes by type breakdown
   - All charts in dark theme matching design system
3. Build `AlertPanel.jsx`:
   - List of predictive alerts from risk module
   - Each alert: severity icon, message, recommended action, dismiss button
   - "Your dispute ratio increased 0.3% this week. Consider adding signature confirmation for orders over $100."
4. Wire analytics API calls

**Success Criteria:** Risk dashboard shows meaningful metrics; charts render with dark theme; alerts display with actionable recommendations.

---

### Day 20 (Nov 6) — Micro-Animations & Responsive Polish

**Tasks:**
1. Add all micro-animations from the strategy:
   - New dispute: card glow pulse + slide-in
   - Agent thinking: rotating gradient border + pulsing icon
   - Evidence submitted: checkmark + subtle particle effect
   - Stat counters: count-up on page load
   - Grid row hover: elevation + highlight
   - Risk alert: slide-in toast with warning pulse
2. Responsive design:
   - Tablet (768px-1024px): stacked layout, grid with fewer columns
   - Mobile (< 768px): card-based simplified view
3. Accessibility check:
   - Keyboard navigation works for grid and panels
   - Sufficient color contrast in dark mode
   - ARIA labels on interactive elements
4. Cross-browser test: Chrome, Firefox, Edge

**Success Criteria:** All animations feel smooth and professional; no jank; responsive layouts work; app feels "alive."

---

### Day 21 (Nov 7) — Integration Testing & APIMatic

**Tasks:**
1. **End-to-end testing:**
   - Run 10 different dispute scenarios through the full pipeline
   - Test: INR with tracking, INR without tracking, SNAD, Unauthorized, edge cases
   - Verify: webhook → agent → evidence → submit → grid update → WebSocket notification
   - Fix any broken flows
2. **APIMatic integration:**
   - Upload PayPal Disputes API OpenAPI spec to APIMatic
   - Generate TypeScript SDK
   - Document in README how APIMatic was used for API context
3. **Code cleanup:**
   - Remove debug logs
   - Consistent formatting (Black for Python, Prettier for JS)
   - Add docstrings to all public functions
   - Ensure all imports are clean
4. **README polish:**
   - Installation steps (Docker and manual)
   - Configuration guide with `.env.example`
   - Architecture diagram (Mermaid)
   - Screenshots placeholder (add real ones after Day 22)

**Success Criteria:** 10/10 test scenarios pass; README is comprehensive; code is clean and documented.

---


## 🚀 Phase 4: Deploy, Demo, Submit (Days 22–26)

### Day 22 (Nov 8) — Render Deployment

**Tasks:**
1. Create `render.yaml` blueprint:
   - Web service: FastAPI backend
   - Background worker: Celery worker
   - PostgreSQL database
   - Environment variables configured
2. Deploy to Render:
   - Push to GitHub → Render auto-deploys
   - Verify webhook endpoint is reachable at `https://disputeshield.onrender.com/webhooks/paypal`
   - Update PayPal Sandbox webhook URL to Render endpoint
   - Test full pipeline on deployed version
3. Seed production database with demo data
4. Take high-quality screenshots of the deployed app (6 screenshots):
   - Dashboard overview with disputes
   - Agent processing a new dispute (mid-action)
   - Evidence submitted successfully
   - Master-detail expanded view
   - Risk dashboard
   - Mobile view (if applicable)

**Success Criteria:** Live URL works; webhook → agent → dashboard pipeline runs on Render; screenshots captured.

---

### Day 23 (Nov 9) — Demo Script & Rehearsal

**Tasks:**
1. Finalize the 3-minute demo script (from strategy document Section 5.1)
2. Set up demo environment:
   - Pre-seed specific dispute data that makes the demo compelling
   - Prepare the sandbox dispute trigger (curl command or UI button)
   - Ensure the demo scenario runs reliably 10/10 times
3. Rehearse 5+ times:
   - Time each run (target: 2:50-2:55)
   - Practice voiceover delivery
   - Identify and fix any demo bugs
   - Note which parts might lag or fail — have backup plan
4. Set up OBS Studio:
   - 1080p recording settings
   - Clean desktop (hide bookmarks, notifications, personal tabs)
   - Audio: separate voiceover track, subtle background music

**Success Criteria:** Demo runs reliably in under 3 minutes; voiceover is smooth; no crashes or long loading times.

---

### Day 24 (Nov 10) — Video Recording

**Tasks:**
1. Record the demo video (minimum 3 takes):
   - Take 1: Full run-through for pacing
   - Take 2: Focus on smooth transitions
   - Take 3: Final polished take
2. Edit video (light editing):
   - Trim dead air
   - Add captions/subtitles (judges may watch muted)
   - Add architecture diagram overlay (30-second flash)
   - Add custom YouTube thumbnail
   - Add "Built with: PayPal MCP, AG Grid, Elasticsearch, LangChain" text card at end
3. Upload to YouTube:
   - Title: "DisputeShield AI — Agentic Dispute Defense for PayPal Merchants"
   - Description: Brief summary + links to GitHub + Devpost
   - Set to **Public** (required)
   - Verify video is under 3 minutes

**Success Criteria:** YouTube video is public, under 3 minutes, 1080p, with captions and custom thumbnail.

---

### Day 25 (Nov 11) — Devpost Submission

**Tasks:**
1. Write Devpost project description (500+ words):
   - **Inspiration:** "Merchants lose 43% of disputes due to late evidence..."
   - **What it does:** Feature list with AI agent, real-time defense, RAG, risk prediction
   - **How we built it:** Tech stack, architecture, PayPal APIs, MCP, AG Grid, Elasticsearch
   - **Challenges:** Webhook reliability, agent guardrails, real-time updates
   - **Accomplishments:** Response time reduction, evidence automation, multi-API integration
   - **What we learned:** MCP protocol, dispute lifecycle, agentic AI patterns
   - **What's next:** Production deployment, merchant onboarding, PayPal Marketplace app

   - **Built With tags:** All technologies listed
2. Attach:
   - YouTube video link
   - GitHub repository link (verify it's public with MIT License)
   - Live demo URL (Render)
   - 4-6 screenshots
3. Select applicable prize categories:
   - Grand Prize
   - Best Use of PayPal + AI
   - Most Impactful
   - AG Grid Bounty
   - Best Demo Delivery
4. Review everything twice

**Success Criteria:** All Devpost fields complete; video + repo + demo links work; screenshots look premium.

---

### Day 26 (Nov 12) — FINAL SUBMISSION

**Tasks:**
1. Final bug check: test the live demo URL one more time ✅ (Frontend & API verified online)
2. Verify all links work (YouTube, GitHub, Render demo) ✅ (All links live & operational)
3. Re-read Devpost submission for typos ✅ (Complete Devpost review finished)
4. **SUBMIT before 12:00 PM PST (1:30 AM IST Nov 13)** ✅ (**OFFICIALLY SUBMITTED ON DEVPOST!**)
5. 🎉 Celebrate ✅ (Day 26 Complete!)

**Success Criteria:** ✅ Submitted. 🏆 [COMPLETED]

---

## 🔑 Critical Success Factors

| Factor | Priority | Validation |
|--------|----------|-----------|
| **PayPal MCP as primary integration** | 🔴 Critical | Agent uses MCP tool-calling, not hardcoded REST |
| **Live webhook → agent → evidence demo** | 🔴 Critical | This is the "wow moment" — must work every time |
| **AG Grid with advanced features** | 🔴 Critical | SSRM + sparklines + custom renderers + master-detail |
| **Premium dark-mode UI** | 🔴 Critical | First impression matters — glassmorphism + animations |
| **Demo video under 3 minutes** | 🔴 Critical | Over 3 min = disqualified |
| **Public GitHub + MIT License** | 🔴 Critical | Missing = disqualified |
| **RAG over dispute history** | 🟡 Important | Unique differentiator — include if time allows |
| **Risk prediction dashboard** | 🟡 Important | Shows depth — include if time allows |
| **APIMatic SDK generation** | 🟢 Nice-to-have | Mention in description even if minimal |
| **Responsive design** | 🟢 Nice-to-have | Judges test on desktop |

---

> [!IMPORTANT]
> ## Emergency Scope Cut Order
> If behind schedule, drop features in this exact order:
> 1. ❌ APIMatic SDK generation (mention it, don't build it)
> 2. ❌ Mobile responsive design
> 3. ❌ Risk prediction dashboard (drop to a static placeholder)

> 4. ❌ RAG similar-case retrieval (agent works without it)
> 5. ⚠️ **NEVER drop:** Webhook → Agent → Evidence pipeline, AG Grid dashboard, Demo video
