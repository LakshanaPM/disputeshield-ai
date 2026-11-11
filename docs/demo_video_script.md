# DisputeShield AI — Spoken Demo Video Script & Post-Production Plan

> **Format:** Spoken video walkthrough (Natural, enthusiastic, founder-style demo)  
> **Duration:** 2 minutes 45 seconds – 2 minutes 55 seconds (Hard limit: Must be under 3:00)  
> **Screen:** `https://disputeshield-frontend-gt1j.onrender.com` (Fullscreen `F11`)  
> **Sponsor Alignment:** PayPal MCP, AG Grid Enterprise, Elasticsearch, LangChain

---

## 🎬 Video Timeline & Narration

### [0:00 – 0:25] The Hook & The Problem
**👉 What you do on screen:**
- Start with the live dashboard already open in Chrome (`F11` fullscreen).
- Move mouse gently across the top cards and AG Grid table.

**🗣️ What you say (Warm, engaging, natural):**
> "Hey everyone!
>
> Did you know that online merchants actually lose almost **half** of all customer disputes... simply because they run out of time?
>
> Think about it: a customer opens a dispute, and PayPal gives you just ten days to respond. Tracking down FedEx tracking numbers, finding delivery signatures, and writing formal legal letters takes 40 to 50 minutes for a single case. For busy sellers, thousands of dollars just slip through the cracks.
>
> That's why we built **DisputeShield AI**—an autonomous defense agent that handles PayPal disputes for you, in real time."

---

### [0:25 – 0:55] The Command Center & AG Grid Drawer
**👉 What you do on screen:**
- Point cursor to the top stats: *22 open claims*, *83.3% win rate*, *$870 protected*.
- Click the **"DISPUTED AMOUNT"** column header twice (shows sorting).
- Click the **"Requires Review / Drafts"** tab, then click back to **"All Disputes"**.
- Click **"Details ⌵"** on row `PP-D-UNAUTH-3002` to open the drawer.

**🗣️ What you say (Conversational, pointing out features):**
> "Right here is the merchant dashboard, built on **AG Grid Enterprise**.
>
> With AG Grid's server-side engine, merchants can easily scroll, sort, and filter through thousands of claims with zero lag.
>
> But watch what happens when I expand any dispute row...
>
> Instantly, AG Grid's master-detail drawer pulls up the entire case:
> Over on the left, we have the order details and the buyer's exact complaint.
> In the middle, live carrier telematics verify that FedEx actually delivered the package to the buyer's zip code, 90210.
> And on the right, our RAG engine automatically matches the case against PayPal's Seller Protection rules."

---

### [0:55 – 1:40] Live Agent In Action (The "Magic" Moment)
**👉 What you do on screen:**
- Scroll down slightly inside the drawer to show the auto-drafted statement.
- Move up to the TopNav and click the blue **"Simulate Webhook"** button.
- A toast notification pops up in the top right.
- Click the **"AI Stream"** button in the top right corner—the drawer slides open!
- Point cursor at the new event and the green checkmarks in the execution chain.

**🗣️ What you say (Excited, dynamic):**
> "Now, let’s see the AI agent in action.
>
> I'm going to simulate a real PayPal webhook arriving right now... *[Click 'Simulate Webhook']*
>
> Boom. A new unauthorized transaction dispute just landed.
>
> Let's open our live **AI Agent Stream** on the right.
>
> Look at what the agent is doing step-by-step:
> It instantly grabs the webhook...
> Uses the Model Context Protocol to query FedEx tracking...
> Verifies the customer's delivery coordinates...
> And pulls similar winning cases from our vector database.
>
> Because confidence is high—88%—the agent doesn't even need to bother the merchant. It signs the evidence, packages it up, and dispatches it straight to the PayPal Resolution API in seconds. Completely hands-free."

---

### [1:40 – 2:10] Human-in-the-Loop & 1-Click Approve
**👉 What you do on screen:**
- Close the sidebar stream (click `✕`).
- In the table, find row `PP-D-UNAUTH-3004` (with the amber badge `Draft (Pending Review)`) and click **"Review & Sign →"**.
- Inside the drawer, click **"Edit Statement"** and type a few words into the box.
- Click the big blue button: **"1-Click Approve & Submit to PayPal API"**.
- The green success banner pops up!
- Click the **Bell icon** in the top bar to show the notification feed.

**🗣️ What you say (Clear, reassuring):**
> "Now, what about tricky cases where the AI isn't 100% sure?
>
> That's where our **Human-in-the-Loop** mode comes in.
>
> Take a look at this case marked *Draft: Pending Review*. The agent gathered all the evidence and wrote a complete defense statement, but it held back from submitting automatically.
>
> As a merchant, I can click *Edit Statement*, add any extra context I want, and when I'm happy, I just hit **1-Click Approve & Submit**.
>
> *[Click button]*
>
> Just like that, it's submitted directly to PayPal. You get total automation for straightforward claims, but full human control whenever you need it."

---

### [2:10 – 2:35] Risk Analytics & Precedent Embeddings
**👉 What you do on screen:**
- Click the **"Risk & Limitation Analytics"** tab in the navigation bar.
- Point to the **Account Health Gauge** (the speedometer) and the 30-day trend chart.
- Toggle the switch on **"Carrier Delay Spike in Midwest"** (it turns green with a toast!).
- Switch back to the **"Dispute Queue"** tab, scroll to the bottom right card, and click **"Explore precedent embeddings ↗"**.
- The modal opens: show the 32 cases and click **"Inspect Vector"** on any row.

**🗣️ What you say (Informative, showing depth):**
> "DisputeShield doesn't just fight disputes—it helps prevent them.
>
> Over on our **Risk Analytics** tab, this live health gauge tracks our dispute ratio against PayPal's critical 1.5% limit.
>
> If there's a delivery delay spike in the Midwest, we can turn on a predictive guardrail with one click to require signature confirmation before chargebacks happen.
>
> And down here, our **Precedent Retrieval Engine** stores 32 historical case embeddings. You can literally explore the 1536-dimensional vector space our AI searches to find winning defense strategies."

---

### [2:35 – 2:50] Architecture Diagram Overlay Flash
**👉 What you do on screen (Video Edit):**
- Overlay the **DisputeShield System Architecture Diagram** over the screen (or Picture-in-Picture) for 15 seconds.
- Graphic shows the flow:
  `PayPal Webhook → FastAPI → LangChain Agent (@paypal/mcp) → Elasticsearch Vector RAG → AG Grid Enterprise UI`

**🗣️ What you say (Authoritative, tech-focused):**
> "Under the hood, DisputeShield combines **PayPal's REST APIs and Model Context Protocol**, **AG Grid Enterprise**, **Elasticsearch Vector Search**, and **LangChain** into a production-ready solution deployed live on Render.
>
> No more missed deadlines. No more lost revenue.
>
> With **DisputeShield AI**, merchants can finally put their dispute defense on autopilot."

---

### [2:50 – 2:55] Sponsor End-Card & Sign-off
**👉 What you do on screen (Video Edit):**
- Fullscreen End-Card appears for the final 5 seconds:
  ```
  ┌───────────────────────────────────────────────────────────┐
  │                    DisputeShield AI                       │
  │        Autonomous PayPal Dispute Defense Platform         │
  │                                                           │
  │  Built with:                                              │
  │  • PayPal Model Context Protocol (@paypal/mcp)            │
  │  • AG Grid Enterprise                                     │
  │  • Elasticsearch 1536-dim Vector RAG                      │
  │  • LangChain & FastAPI                                    │
  │                                                           │
  │  GitHub: github.com/LakshanaPM/disputeshield-ai           │
  │  Demo: disputeshield-frontend-gt1j.onrender.com           │
  └───────────────────────────────────────────────────────────┘
  ```

**🗣️ What you say:**
> "Thanks so much for watching!"

---

## 🛠️ Post-Production & Editing Checklist (Execution Plan Day 24)

Following **Day 24 of the DisputeShield Execution Plan**, apply these 5 quick editing steps before submitting:

### 1. ✂️ Trim Dead Air
- In your video editor (CapCut, Premiere, or Windows Clipchamp), cut out:
  - Any pauses longer than 1.5 seconds.
  - Awkward mouse searching or loading delays.
  - Keep the tempo brisk and energetic. Ensure total runtime is between **2:45 and 2:55**.

### 2. 💬 Add Captions / Subtitles (Critical for Muted Judges)
- **Why:** 60%+ of hackathon evaluators watch demo videos on mute or low volume.
- **How:**
  - Auto-generate captions in CapCut/Clipchamp, OR
  - Upload the video to YouTube and verify YouTube's automatic captions, OR upload an `.srt` file.
  - Style: Clean white text with a subtle dark outline or box at the bottom center.

### 3. 🖼️ Architecture Diagram Overlay (Flash at 2:35)
- Insert a clean architecture graphic at **[2:35 – 2:45]** while discussing the tech stack.
- Elements to display in the graphic:
  1. `PayPal Webhook Ingest (FastAPI)`
  2. `Model Context Protocol (@paypal/mcp Tools)`
  3. `Elasticsearch Precedent Vectors (1536-dim RAG)`
  4. `AG Grid Enterprise SSRM Data Grid`
  5. `WebSocket Real-Time Broadcast`

### 4. 🎨 Custom YouTube Thumbnail
- **Dimensions:** 1280 x 720 (16:9), PNG or JPG under 2MB.
- **Layout:**
  - **Left 60%:** Screenshot of the AG Grid Command Center + Emerald "Auto-Dispatched" badge.
  - **Right 40%:** DisputeShield Shield Logo + Bold text: **"AUTONOMOUS PAYPAL DEFENSE"** in high-contrast white & gold.
  - **Top Corner:** "PayPal AI Hackathon 2026" badge.

### 5. 🏷️ "Built With" End Text Card (Last 5 Seconds)
- Insert the static title card at **[2:50 – 2:55]** displaying:
  **"Built with: PayPal MCP, AG Grid, Elasticsearch, LangChain"**
  along with your GitHub repository link: `github.com/LakshanaPM/disputeshield-ai`.
