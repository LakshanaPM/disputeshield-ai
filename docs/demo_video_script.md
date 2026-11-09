# DisputeShield AI — Spoken Demo Video Script (Conversational & Natural)

> **Format:** Spoken video walkthrough (Natural, enthusiastic, founder-style demo)  
> **Duration:** ~2 minutes 45 seconds (Safe margin under the 3-minute hard limit)  
> **Screen:** `https://disputeshield-frontend-gt1j.onrender.com` (Fullscreen `F11`)  
> **Tip:** Read naturally like you are talking to a colleague or hackathon judge. Don't rush! Pauses (`...`) are marked for natural breathing.

---

## 🎙️ Spoken Script & Screen Actions

### [0:00 – 0:25] The Hook & The Problem
**👉 What you do on screen:**
- Start with the live dashboard already open in Chrome (`F11` fullscreen).
- Gently move your mouse over the top cards and the table.

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

### [2:35 – 2:55] Closing & Wrap Up
**👉 What you do on screen:**
- Close the modal (`✕`) so you are back on the clean, beautiful main dashboard.
- Mouse rests near the logo. Hold the screen steady.

**🗣️ What you say (Warm, punchy closing):**
> "Under the hood, DisputeShield combines **PayPal's APIs and Model Context Protocol**, **AG Grid Enterprise**, and **Vector RAG** into a production-ready solution deployed live on Render.
>
> No more missed deadlines. No more lost revenue.
>
> With **DisputeShield AI**, merchants can finally put their dispute defense on autopilot.
>
> Thanks so much for watching!"

---

## 💡 Quick Tips for a Flawless Recording
1. **Talk to a person:** Imagine you are showing this to a friend on a Zoom call. Smile while speaking—it actually makes your voice sound warmer!
2. **Don't rush the clicks:** After you click a button (like *Simulate Webhook* or *Approve*), pause for 1 second so the viewer can see the toast or banner appear before you start talking about it.
3. **If you make a mistake:** Don't restart the whole video! Just pause for 3 seconds, take a breath, and re-read that one sentence. You can easily cut out the silence in any free editor (like CapCut, Clipchamp, or Premiere).
4. **Timer Check:** Practice once with a phone stopwatch. Aiming for around **2 minutes 45 seconds** gives you plenty of safety under the 3-minute cutoff.
