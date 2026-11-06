
# DisputeShield AI — 3-Minute Demo Video Script (Shark Tank Format)

> **Target Duration:** 2 minutes 45 seconds – 2 minutes 55 seconds  
> **Resolution:** 1080p (60fps recommended)  
> **Key Visuals:** DisputeShield UI, AG Grid Enterprise Drawer, Live Agent Execution, PayPal Resolution Dispatch

---

### [0:00 - 0:25] The Hook & The Problem
**Visual:** Screen starts on clean desktop; mouse cursor opens DisputeShield AI dashboard (`http://localhost:5173` or live Render URL). The high-contrast PayPal Dual-Blue TopNav and AG Grid load crisply.

**Voiceover (Confident, energetic):**
> "Every single day, online merchants lose **43% of customer disputes**—not because their products are faulty, but because they simply run out of time to collect evidence before PayPal's 10-day deadline expires.
>
> Collecting FedEx tracking receipts, customer support emails, and signed invoices takes up to 45 minutes per dispute. For high-volume sellers, this is an operational nightmare costing billions in lost revenue.
>
> Meet **DisputeShield AI**—the autonomous dispute defense agent built specifically for PayPal merchants."

---

### [0:25 - 0:50] The AG Grid Command Center
**Visual:** Camera pans over the Stat Cards (`$248,500 Protected Revenue`, `89.4% Win Rate`, `45s Avg Response Time`). Scroll smoothly down to the **AG Grid Enterprise** table. Click a column header to demonstrate multi-column sorting, then expand a row drawer.

**Voiceover:**
> "Here is the merchant command center, powered by **AG Grid Enterprise**.
>
> Using AG Grid's Server-Side Row Model, merchants can monitor tens of thousands of active dispute claims with sub-millisecond sorting, filtering, and real-time status updates.
>
> When we expand any dispute row using AG Grid's Master-Detail drawer, we immediately see the complete audit trail: the customer's claim, transaction details, and the historical dispute lifecycle."

---

### [0:50 - 1:40] The Live Agent In Action (The "Magic" Moment)
**Visual:** Move mouse to top navigation bar. Click the **"Simulate Webhook & Agent Run"** button.  
Switch to the **"Agent Reasoning Stream"** tab.  
The live WebSocket feeds step-by-step agent telemetry in real time:
1. `Webhook received: CUSTOMER.DISPUTE.CREATED (PP-D-84920)`
2. `MCP Tool Invocation: fetch_carrier_tracking(FedEx #794612349876) -> DELIVERED`
3. `Deterministic Policy Check: PayPal Seller Protection -> ELIGIBLE`
4. `Confidence Scorer: Evaluated 5 dimensions -> 94% WIN PROBABILITY`
5. Status Banner updates: `Rebuttal Dispatched to PayPal Resolution API` with `Auto-Dispatched` emerald badge!

**Voiceover:**
> "Now let's watch the agent in action. A customer has just opened an *Unauthorized Transaction* dispute for a $389.00 order.
>
> Instantly, DisputeShield's backend verifies the PayPal webhook signature and wakes up our autonomous LangChain agent.
>
> Watch the live reasoning trace: via the **Model Context Protocol (MCP)**, the agent queries FedEx logistics tools in real time. It discovers that the package was signed by the customer at the verified PayPal shipping address.
>
> Next, our deterministic confidence engine evaluates the evidence against PayPal's Seller Protection rules. The result: **94% win confidence**—exceeding our 85% autonomous threshold.
>
> Within 12 seconds, the agent drafts an airtight legal rebuttal, attaches the carrier receipt, and dispatches it directly to the PayPal Dispute Resolution API. No human intervention needed."

---

### [1:40 - 2:10] Human-in-the-Loop & Interactive Drawer
**Visual:** Click the **"Disputes Grid"** tab. Filter to a dispute with amber badge `Pending Approval` (confidence 74%). Click the row to expand the detail drawer. Show the generated rebuttal text, the Evidence Checklist with yellow warnings, and the prominent **"Approve & Submit Rebuttal"** button.

**Voiceover:**
> "What about ambiguous cases? When confidence falls below 85%—for example, when an item is claimed as 'Significantly Not As Described'—DisputeShield never gambles with merchant reputation.
>
> Instead, it stages an interactive defense packet. Merchants see clear missing evidence callouts, can edit the AI-generated rebuttal draft, and click 'Approve & Submit' with a single tap. Complete automation when confidence is high; complete control when it counts."

---

### [2:10 - 2:35] Predictive Risk & Portfolio Forensics
**Visual:** Click the **"Risk Forensics"** tab in the top navigation. The radial Risk Gauge animates, showing the merchant's dispute rate at `0.42%` (comfortably below PayPal's `1.0%` threshold). Highlight the Trend Chart and Reason Breakdown.

**Voiceover:**
> "Finally, prevention is better than cure. Our **Risk Forensics Dashboard** tracks the merchant's global dispute rate in real time against PayPal's critical 1% monitoring threshold.
>
> Powered by Elasticsearch and predictive heuristics, merchants get early warnings on spike trends, fraud clusters, and high-risk SKUs before chargebacks damage their merchant standing."

---

### [2:35 - 2:55] Architecture & Closing Pitch
**Visual:** Flash the Clean Architecture Diagram (Frontend $\leftrightarrow$ FastAPI $\leftrightarrow$ Celery/PostgreSQL $\leftrightarrow$ Gemini 1.5 $\leftrightarrow$ PayPal MCP $\leftrightarrow$ AG Grid Enterprise). End on the DisputeShield logo with GitHub and Devpost links.

**Voiceover (Strong, memorable finish):**
> "Under the hood, DisputeShield AI combines **PayPal APIs**, the **Model Context Protocol**, **Google Gemini**, and **AG Grid Enterprise** into an end-to-end production solution with multi-language TypeScript and Python SDKs.
>
> Stop bleeding revenue to missed deadlines. Protect your bottom line with **DisputeShield AI**—autonomous dispute defense that never sleeps.
>
> Thank you."

---

### 🎥 OBS Studio Recording Checklist:
- [ ] Display resolution: 1920x1080, 60fps, Bitrate 12,000 kbps.
- [ ] Browser zoom: 100% or 110% (ensure all AG Grid text and cards are crisp).
- [ ] Clean desktop: Close Slack, Discord, email, WhatsApp, and browser bookmarks bar.
- [ ] Seed fresh data: Run `python scripts/seed_demo_disputes.py` before Take 1.
- [ ] Audio: Test mic gain; ensure zero background noise or fan hum.

