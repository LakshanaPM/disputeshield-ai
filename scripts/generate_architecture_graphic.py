"""
DisputeShield AI — Broadcast Graphic Suite Generator (Exact Project Theme & Real Logo)

Embeds:
- frontend/src/assets/logo.png
- frontend/src/assets/shield.png
Theme:
- PayPal Dual-Blue Light Enterprise Theme (#F8FAFC slate background, #FFFFFF cards, #00457C navy, #0079C1 marine blue)
"""

import base64
import os
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = ROOT / "docs" / "screenshots"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
EDGE_BIN = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

# 1. Read and base64-encode the actual project logos
logo_path = ROOT / "frontend" / "src" / "assets" / "logo.png"
shield_path = ROOT / "frontend" / "src" / "assets" / "shield.png"

with open(logo_path, "rb") as f:
    logo_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

with open(shield_path, "rb") as f:
    shield_b64 = f"data:image/png;base64,{base64.b64encode(f.read()).decode('utf-8')}"

# ==============================================================================
# 1. System Architecture Diagram HTML (1920x1080 - PayPal Dual-Blue Light Theme)
# ==============================================================================
architecture_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DisputeShield AI — System Architecture</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&display=swap');
    
    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      width: 1920px;
      height: 1080px;
      background: #F8FAFC;
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      color: #0F172A;
      overflow: hidden;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
    }}

    /* Top Navigation Header matching frontend TopNav.jsx */
    .top-header {{
      background: #FFFFFF;
      border-bottom: 1px solid #E2E8F0;
      height: 96px;
      padding: 0 60px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}

    .brand-left {{
      display: flex;
      align-items: center;
      gap: 20px;
    }}

    .brand-left img.logo {{
      height: 48px;
      width: auto;
      object-contain: contain;
    }}

    .tagline {{
      font-size: 13px;
      font-weight: 600;
      color: #64748B;
      border-left: 2px solid #E2E8F0;
      padding-left: 18px;
      letter-spacing: -0.2px;
    }}

    .header-telemetry {{
      display: flex;
      align-items: center;
      gap: 14px;
    }}

    .telemetry-pill {{
      display: flex;
      align-items: center;
      gap: 8px;
      padding: 8px 16px;
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 700;
      color: #334155;
    }}

    .dot-live {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #10B981;
      box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.2);
    }}

    .health-badge {{
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 18px;
      background: #EFF6FF;
      border: 1px solid #BFDBFE;
      border-radius: 9999px;
      font-size: 12px;
      font-weight: 800;
      color: #00457C;
    }}

    .health-badge span.ratio {{
      color: #0079C1;
      font-family: 'JetBrains Mono', monospace;
    }}

    .sponsors-bar {{
      display: flex;
      gap: 10px;
    }}

    .sponsor-tag {{
      font-size: 11px;
      font-weight: 800;
      padding: 6px 12px;
      border-radius: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .sponsor-tag.paypal {{ background: #E0F2FE; color: #0079C1; border: 1px solid #BAE6FD; }}
    .sponsor-tag.aggrid {{ background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA; }}
    .sponsor-tag.elastic {{ background: #FEF9C3; color: #B45309; border: 1px solid #FDE68A; }}
    .sponsor-tag.langchain {{ background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0; }}

    /* Main Diagram Content */
    .content-area {{
      padding: 30px 60px;
      flex: 1;
      display: flex;
      flex-direction: column;
      justify-content: space-around;
    }}

    .section-title-row {{
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
      margin-bottom: 20px;
    }}

    .section-title-row h2 {{
      font-size: 26px;
      font-weight: 900;
      color: #0F172A;
      letter-spacing: -0.5px;
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .section-title-row h2 span.sub {{
      color: #0079C1;
    }}

    .section-title-row p {{
      font-size: 14px;
      color: #64748B;
      font-weight: 500;
      margin-top: 4px;
    }}

    .architecture-flow {{
      display: grid;
      grid-template-columns: 370px 48px 410px 48px 390px 48px 430px;
      align-items: center;
      gap: 0;
    }}

    /* Architecture Stage Cards */
    .stage-card {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 18px;
      padding: 24px 22px;
      box-shadow: 0 4px 12px rgba(15, 23, 42, 0.05);
      display: flex;
      flex-direction: column;
      gap: 14px;
      position: relative;
    }}

    .stage-card.paypal {{ border-top: 4px solid #0079C1; }}
    .stage-card.agent {{ border-top: 4px solid #00457C; }}
    .stage-card.rag {{ border-top: 4px solid #D97706; }}
    .stage-card.aggrid {{ border-top: 4px solid #059669; }}

    .stage-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #F1F5F9;
    }}

    .stage-number-title {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}

    .stage-icon {{
      width: 32px;
      height: 32px;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 900;
      font-size: 14px;
    }}

    .stage-card.paypal .stage-icon {{ background: #E0F2FE; color: #0079C1; }}
    .stage-card.agent .stage-icon {{ background: #EBF5FF; color: #00457C; }}
    .stage-card.rag .stage-icon {{ background: #FEF3C7; color: #D97706; }}
    .stage-card.aggrid .stage-icon {{ background: #D1FAE5; color: #059669; }}

    .stage-title {{
      font-size: 14px;
      font-weight: 800;
      color: #0F172A;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .stage-badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 11px;
      font-weight: 800;
      padding: 3px 8px;
      border-radius: 6px;
      background: #F1F5F9;
      color: #475569;
    }}

    /* Module Blocks Inside Stages */
    .module-box {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 12px;
      padding: 12px 14px;
      display: flex;
      flex-direction: column;
      gap: 3px;
    }}

    .module-name {{
      font-size: 13px;
      font-weight: 800;
      color: #0F172A;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }}

    .module-desc {{
      font-size: 11px;
      color: #64748B;
      line-height: 1.4;
    }}

    .tag-mono {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      font-weight: 700;
      color: #0079C1;
      background: #EBF8FF;
      padding: 2px 6px;
      border-radius: 4px;
      align-self: flex-start;
      margin-top: 4px;
      border: 1px solid #BAE6FD;
    }}

    /* Flow Connectors */
    .flow-connector {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
    }}

    .flow-connector svg {{
      width: 28px;
      height: 28px;
      stroke: #0079C1;
      fill: none;
      stroke-width: 2.5;
    }}

    .connector-text {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 9px;
      font-weight: 800;
      color: #64748B;
      text-transform: uppercase;
      letter-spacing: 0.5px;
      margin-top: 4px;
      white-space: nowrap;
    }}

    /* Bottom KPI Ribbon (Matching StatCards.jsx) */
    .bottom-ribbon {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      margin-top: 15px;
    }}

    .kpi-card {{
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 14px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    }}

    .kpi-label {{
      font-size: 11px;
      font-weight: 700;
      color: #64748B;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .kpi-val {{
      font-size: 24px;
      font-weight: 900;
      font-family: 'JetBrains Mono', monospace;
      color: #0F172A;
      margin-top: 2px;
    }}

    .kpi-sub {{
      font-size: 11px;
      font-weight: 600;
      color: #10B981;
    }}

    /* Bottom Footer Bar */
    .footer-bar {{
      background: #FFFFFF;
      border-top: 1px solid #E2E8F0;
      height: 52px;
      padding: 0 60px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      font-size: 12px;
      font-weight: 600;
      color: #64748B;
    }}

    .footer-left {{
      display: flex;
      align-items: center;
      gap: 16px;
    }}

    .footer-verified {{
      display: flex;
      align-items: center;
      gap: 6px;
      color: #059669;
      font-weight: 800;
      background: #ECFDF5;
      padding: 4px 12px;
      border-radius: 6px;
      border: 1px solid #A7F3D0;
    }}
  </style>
</head>
<body>
  <!-- Top Navigation Header (Exact look of DisputeShield TopNav) -->
  <header class="top-header">
    <div class="brand-left">
      <img src="{logo_b64}" alt="DisputeShield AI" class="logo" />
      <span class="tagline">Autonomous PayPal Defense System Architecture</span>
    </div>

    <div class="header-telemetry">
      <div class="telemetry-pill">
        <span class="dot-live"></span>
        <span>Agent Live • 42ms Latency</span>
      </div>

      <div class="health-badge">
        <span>Health Score: <strong>76/100</strong></span>
        <span>|</span>
        <span>Dispute Ratio: <span class="ratio">0.80%</span></span>
        <span>|</span>
        <span style="color: #059669;">SAFE HARBOR</span>
      </div>

      <div class="sponsors-bar">
        <span class="sponsor-tag paypal">PayPal MCP</span>
        <span class="sponsor-tag aggrid">AG Grid Enterprise</span>
        <span class="sponsor-tag elastic">Elasticsearch RAG</span>
        <span class="sponsor-tag langchain">LangChain</span>
      </div>
    </div>
  </header>

  <!-- Content Area -->
  <div class="content-area">
    <div class="section-title-row">
      <div>
        <h2>System Architecture &amp; Autonomous Pipeline <span class="sub">• Real-Time Telemetry Flow</span></h2>
        <p>End-to-end multi-agent dispute triage, carrier telematics verification, 1536-dim vector precedents, and AG Grid SSRM command center.</p>
      </div>
      <div style="font-family: 'JetBrains Mono', monospace; font-size: 12px; color: #0079C1; font-weight: 700;">
        FastAPI • PostgreSQL • WebSockets • Render Deployed
      </div>
    </div>

    <!-- 4-Stage Architecture Flow Grid -->
    <div class="architecture-flow">
      <!-- 1. Webhook Ingest -->
      <div class="stage-card paypal">
        <div class="stage-header">
          <div class="stage-number-title">
            <div class="stage-icon">1</div>
            <div class="stage-title">Ingestion &amp; Sync</div>
          </div>
          <span class="stage-badge">FASTAPI</span>
        </div>

        <div class="module-box">
          <div class="module-name">
            <span>PayPal Dispute Webhook</span>
            <span style="color: #059669; font-size: 11px;">CRC32 / RSA</span>
          </div>
          <div class="module-desc">Listens for CUSTOMER.DISPUTE.CREATED events with signature verification.</div>
          <span class="tag-mono">POST /api/webhooks/paypal</span>
        </div>

        <div class="module-box">
          <div class="module-name">Async Event Dispatcher</div>
          <div class="module-desc">Sub-200ms ACK returned to PayPal Event Bus; background task enqueued.</div>
          <span class="tag-mono">FastAPI BackgroundTasks</span>
        </div>

        <div class="module-box">
          <div class="module-name">PayPal Sandbox Mirror</div>
          <div class="module-desc">Live bi-directional dispute state synchronization with remote sandbox claims.</div>
          <span class="tag-mono">POST /api/disputes/sync-sandbox</span>
        </div>
      </div>

      <!-- Connector 1 -->
      <div class="flow-connector">
        <svg viewBox="0 0 24 24"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
        <span class="connector-text">Payload</span>
      </div>

      <!-- 2. LangChain & MCP Agent -->
      <div class="stage-card agent">
        <div class="stage-header">
          <div class="stage-number-title">
            <div class="stage-icon">2</div>
            <div class="stage-title">Autonomous Agent</div>
          </div>
          <span class="stage-badge">MCP TOOLS</span>
        </div>

        <div class="module-box">
          <div class="module-name">
            <span>Model Context Protocol</span>
            <span style="color: #0079C1; font-size: 10px;">@paypal/mcp</span>
          </div>
          <div class="module-desc">Stdio protocol powering tools: fetch_carrier_tracking, query_order, &amp; verify_identity.</div>
          <span class="tag-mono">@paypal/mcp stdio server</span>
        </div>

        <div class="module-box">
          <div class="module-name">Multi-Agent Triage Engine</div>
          <div class="module-desc">Evaluates claim severity and dispute category: INR, SNAD, or Unauthorized.</div>
          <span class="tag-mono">LangChain + Claude 3.5 / Gemini</span>
        </div>

        <div class="module-box">
          <div class="module-name">5-Dim Confidence Matrix</div>
          <div class="module-desc">
            <strong style="color: #059669;">&ge;80%</strong> Auto-Submit | 
            <strong style="color: #D97706;">60-79%</strong> Human-in-Loop | 
            <strong style="color: #DC2626;">&lt;60%</strong> Escalate
          </div>
          <span class="tag-mono">ConfidenceScorer Engine</span>
        </div>
      </div>

      <!-- Connector 2 -->
      <div class="flow-connector">
        <svg viewBox="0 0 24 24"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
        <span class="connector-text">Vectors</span>
      </div>

      <!-- 3. Dense Vector RAG -->
      <div class="stage-card rag">
        <div class="stage-header">
          <div class="stage-number-title">
            <div class="stage-icon">3</div>
            <div class="stage-title">Vector RAG Engine</div>
          </div>
          <span class="stage-badge">ELASTIC 8.15</span>
        </div>

        <div class="module-box">
          <div class="module-name">
            <span>1536-Dim Dense Vectors</span>
            <span style="color: #D97706; font-size: 10px;">kNN Search</span>
          </div>
          <div class="module-desc">Cosine similarity index over historical won precedents in Elasticsearch.</div>
          <span class="tag-mono">GET /api/analytics/precedents</span>
        </div>

        <div class="module-box">
          <div class="module-name">32 Indexed Case Precedents</div>
          <div class="module-desc">Empirical win rates: 91.2% INR, 73.5% SNAD, 85.7% Unauthorized.</div>
          <span class="tag-mono">Indexed Precedents Library</span>
        </div>

        <div class="module-box">
          <div class="module-name">PayPal Policy §11.3 Citations</div>
          <div class="module-desc">Synthesizes GPS geofence telematics, direct signatures, &amp; SHA-256 evidence packet.</div>
          <span class="tag-mono">Formal Dispute Defense Statement</span>
        </div>
      </div>

      <!-- Connector 3 -->
      <div class="flow-connector">
        <svg viewBox="0 0 24 24"><path d="M5 12h14m-7-7 7 7-7 7"/></svg>
        <span class="connector-text">WebSocket</span>
      </div>

      <!-- 4. AG Grid Command Center -->
      <div class="stage-card aggrid">
        <div class="stage-header">
          <div class="stage-number-title">
            <div class="stage-icon">4</div>
            <div class="stage-title">AG Grid Command</div>
          </div>
          <span class="stage-badge">ENTERPRISE</span>
        </div>

        <div class="module-box">
          <div class="module-name">
            <span>Server-Side Row Model (SSRM)</span>
            <span style="color: #059669; font-size: 10px;">v36.2</span>
          </div>
          <div class="module-desc">Instant sorting, multi-category filtering, &amp; pagination over 50,000+ disputes.</div>
          <span class="tag-mono">AG Grid Enterprise SSRM</span>
        </div>

        <div class="module-box">
          <div class="module-name">Master-Detail Dispute Drawer</div>
          <div class="module-desc">Interactive 3-column verification matrix with 1-Click Approve &amp; Rebuttal Override.</div>
          <span class="tag-mono">POST /api/disputes/{{id}}/approve</span>
        </div>

        <div class="module-box">
          <div class="module-name">Predictive Risk Forensics</div>
          <div class="module-desc">Radial speedometer health gauge, 30-day velocity trajectory, &amp; guardrail toggles.</div>
          <span class="tag-mono">PayPal 1.5% Limitation Guard</span>
        </div>
      </div>
    </div>

    <!-- Bottom Stat KPI Ribbon (Matching Frontend StatCards.jsx) -->
    <div class="bottom-ribbon">
      <div class="kpi-card">
        <div>
          <div class="kpi-label">Total Active Disputes</div>
          <div class="kpi-val">22 claims</div>
        </div>
        <span class="footer-verified" style="font-size: 11px;">Live Queue</span>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">Merchant Win Rate</div>
          <div class="kpi-val" style="color: #0079C1;">83.3%</div>
        </div>
        <div class="kpi-sub">+30.5% alpha vs 52% avg</div>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">Capital Protected</div>
          <div class="kpi-val" style="color: #059669;">$870.00</div>
        </div>
        <div class="kpi-sub">20.5% salvage of $4.2K</div>
      </div>

      <div class="kpi-card">
        <div>
          <div class="kpi-label">90-Day Dispute Velocity</div>
          <div class="kpi-val" style="color: #D97706;">0.80%</div>
        </div>
        <div style="font-size: 11px; font-weight: 700; color: #64748B;">/ 1.50% ceiling</div>
      </div>
    </div>
  </div>

  <!-- Bottom Footer Bar -->
  <footer class="footer-bar">
    <div class="footer-left">
      <div class="footer-verified">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>
        <span>Production Deployed on Render</span>
      </div>
      <span>•</span>
      <span>PostgreSQL 16 Cloud DB</span>
      <span>•</span>
      <span>39/39 Passing Pytest Tests</span>
      <span>•</span>
      <span>0 Build Errors</span>
    </div>

    <div>
      <strong>Target Prizes:</strong> Grand Prize ($12,000) • AG Grid Bounty ($5,000) • Best Use of PayPal + AI ($5,000)
    </div>
  </footer>
</body>
</html>
"""

# ==============================================================================
# 2. Sponsor End Card HTML (1920x1080 - PayPal Dual-Blue Light Theme)
# ==============================================================================
endcard_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DisputeShield AI — Sponsor End Card</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800;900&family=JetBrains+Mono:wght@600;800&display=swap');
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      width: 1920px;
      height: 1080px;
      background: #F8FAFC;
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #0F172A;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      position: relative;
    }}

    .card {{
      width: 1380px;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 28px;
      padding: 60px 80px;
      box-shadow: 0 20px 45px rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
      align-items: center;
      text-align: center;
      gap: 36px;
    }}

    .logo-img {{
      height: 72px;
      width: auto;
      object-fit: contain;
    }}

    .titles h1 {{
      font-size: 44px;
      font-weight: 900;
      letter-spacing: -1px;
      color: #0F172A;
      margin-top: 10px;
      margin-bottom: 8px;
    }}

    .titles h1 span {{
      color: #0079C1;
    }}

    .titles p {{
      font-size: 19px;
      color: #64748B;
      font-weight: 600;
    }}

    .sponsors-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 20px;
      width: 100%;
    }}

    .sponsor-box {{
      background: #F8FAFC;
      border: 1px solid #E2E8F0;
      border-radius: 18px;
      padding: 24px 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;
      text-align: left;
    }}

    .sponsor-box.paypal {{ border-top: 4px solid #0079C1; }}
    .sponsor-box.aggrid {{ border-top: 4px solid #DC2626; }}
    .sponsor-box.elastic {{ border-top: 4px solid #D97706; }}
    .sponsor-box.langchain {{ border-top: 4px solid #059669; }}

    .sponsor-tag {{
      font-size: 11px;
      font-family: 'JetBrains Mono', monospace;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
    }}

    .paypal .sponsor-tag {{ color: #0079C1; }}
    .aggrid .sponsor-tag {{ color: #DC2626; }}
    .elastic .sponsor-tag {{ color: #D97706; }}
    .langchain .sponsor-tag {{ color: #059669; }}

    .sponsor-name {{
      font-size: 16px;
      font-weight: 800;
      color: #0F172A;
    }}

    .sponsor-desc {{
      font-size: 12px;
      color: #64748B;
      line-height: 1.45;
    }}

    .links-bar {{
      display: flex;
      justify-content: space-between;
      width: 100%;
      padding-top: 24px;
      border-top: 1px solid #E2E8F0;
      font-family: 'JetBrains Mono', monospace;
      font-size: 15px;
      font-weight: 800;
    }}

    .link-pill {{
      color: #00457C;
      background: #EFF6FF;
      padding: 12px 26px;
      border-radius: 12px;
      border: 1px solid #BFDBFE;
    }}
  </style>
</head>
<body>
  <div class="card">
    <img src="{logo_b64}" alt="DisputeShield AI" class="logo-img" />

    <div class="titles">
      <h1>Autonomous PayPal Dispute Defense <span>Platform</span></h1>
      <p>Built for the PayPal AI Hackathon 2026 • Grand Prize &amp; AG Grid Sponsor Bounty Target</p>
    </div>

    <div class="sponsors-grid">
      <div class="sponsor-box paypal">
        <span class="sponsor-tag">Primary Integration</span>
        <span class="sponsor-name">PayPal Model Context Protocol</span>
        <span class="sponsor-desc">@paypal/mcp stdio tool-calling for order telematics, tracking validation, &amp; resolution filing.</span>
      </div>

      <div class="sponsor-box aggrid">
        <span class="sponsor-tag">Sponsor Bounty Target</span>
        <span class="sponsor-name">AG Grid Enterprise v36.2</span>
        <span class="sponsor-desc">Server-Side Row Model (SSRM), Master-Detail drawers, custom cell renderers, &amp; sparklines.</span>
      </div>

      <div class="sponsor-box elastic">
        <span class="sponsor-tag">Precedent Retrieval</span>
        <span class="sponsor-name">Elasticsearch Vector RAG</span>
        <span class="sponsor-desc">1536-dim dense vector search over 32 historical cases with verified Seller Protection clauses.</span>
      </div>

      <div class="sponsor-box langchain">
        <span class="sponsor-tag">Agent Architecture</span>
        <span class="sponsor-name">LangChain &amp; FastAPI</span>
        <span class="sponsor-desc">Deterministic 5-dimension confidence engine, sub-200ms webhooks, and live WebSockets.</span>
      </div>
    </div>

    <div class="links-bar">
      <div class="link-pill">GitHub: github.com/LakshanaPM/disputeshield-ai</div>
      <div class="link-pill" style="color: #059669; border-color: #A7F3D0; background: #ECFDF5;">
        Live Demo: disputeshield-frontend-gt1j.onrender.com
      </div>
    </div>
  </div>
</body>
</html>
"""

# ==============================================================================
# 3. YouTube Thumbnail HTML (1280x720 - PayPal Dual-Blue Light Theme)
# ==============================================================================
thumbnail_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>DisputeShield AI — YouTube Thumbnail</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@700;800;900&family=JetBrains+Mono:wght@800&display=swap');
    
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}

    body {{
      width: 1280px;
      height: 720px;
      background: #F8FAFC;
      font-family: 'Plus Jakarta Sans', sans-serif;
      color: #0F172A;
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 50px 70px;
      position: relative;
    }}

    .left {{
      max-width: 680px;
      display: flex;
      flex-direction: column;
      gap: 22px;
    }}

    .badge-row {{
      display: flex;
      gap: 10px;
    }}

    .badge {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 13px;
      font-weight: 800;
      padding: 6px 14px;
      border-radius: 8px;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    .badge.hackathon {{
      background: #EFF6FF;
      border: 1px solid #BFDBFE;
      color: #00457C;
    }}

    .badge.bounty {{
      background: #FEF2F2;
      border: 1px solid #FECACA;
      color: #DC2626;
    }}

    .logo-thumb {{
      height: 54px;
      width: auto;
      object-fit: contain;
      align-self: flex-start;
    }}

    h1 {{
      font-size: 56px;
      font-weight: 900;
      line-height: 1.08;
      letter-spacing: -1.5px;
      color: #0F172A;
    }}

    h1 span.blue {{
      color: #0079C1;
    }}

    p {{
      font-size: 18px;
      color: #64748B;
      font-weight: 600;
      line-height: 1.4;
    }}

    .pills-strip {{
      display: flex;
      gap: 14px;
      font-size: 13px;
      font-weight: 800;
      color: #334155;
    }}

    .right-card {{
      width: 440px;
      background: #FFFFFF;
      border: 1px solid #E2E8F0;
      border-radius: 24px;
      padding: 34px;
      box-shadow: 0 15px 35px rgba(0, 0, 0, 0.08);
      display: flex;
      flex-direction: column;
      gap: 20px;
    }}

    .card-top {{
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 14px;
      border-bottom: 1px solid #F1F5F9;
    }}

    .card-top img {{
      height: 38px;
      width: 38px;
      object-fit: contain;
    }}

    .metric-row {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding-bottom: 12px;
      border-bottom: 1px solid #F1F5F9;
    }}

    .metric-label {{ font-size: 13px; color: #64748B; font-weight: 700; }}
    .metric-val {{ font-size: 22px; font-family: 'JetBrains Mono', monospace; font-weight: 800; color: #0F172A; }}

    .emerald-badge {{
      background: #ECFDF5;
      border: 1px solid #A7F3D0;
      color: #059669;
      padding: 12px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 800;
      text-align: center;
      letter-spacing: 0.5px;
    }}
  </style>
</head>
<body>
  <div class="left">
    <img src="{logo_b64}" alt="DisputeShield AI" class="logo-thumb" />

    <div class="badge-row">
      <div class="badge hackathon">🏆 PayPal AI Hackathon 2026</div>
      <div class="badge bounty">AG Grid Sponsor Bounty</div>
    </div>

    <h1>Autonomous PayPal<br><span class="blue">Dispute Defense Agent</span></h1>

    <p>Zero-touch evidence compilation, Model Context Protocol, 1536-dim Vector RAG, and AG Grid Enterprise SSRM.</p>

    <div class="pills-strip">
      <span>● PayPal MCP</span>
      <span>● AG Grid SSRM</span>
      <span>● LangChain</span>
      <span>● 83.3% Win Rate</span>
    </div>
  </div>

  <div class="right-card">
    <div class="card-top">
      <img src="{shield_b64}" alt="Shield" />
      <div>
        <div style="font-size: 14px; font-weight: 800; color: #00457C;">Autonomous Defense Matrix</div>
        <div style="font-size: 11px; color: #64748B; font-weight: 600;">PayPal Protection Protocol §11.3</div>
      </div>
    </div>

    <div class="metric-row">
      <span class="metric-label">Triage &amp; File Velocity:</span>
      <span class="metric-val" style="color: #0079C1;">sub-12s</span>
    </div>

    <div class="metric-row">
      <span class="metric-label">Empirical Win Alpha:</span>
      <span class="metric-val" style="color: #059669;">83.3% (+30.5%)</span>
    </div>

    <div class="metric-row">
      <span class="metric-label">Account Health:</span>
      <span class="metric-val">76 / 100</span>
    </div>

    <div class="emerald-badge">
      ✓ Rebuttal Auto-Dispatched
    </div>
  </div>
</body>
</html>
"""

# Write HTML files
arch_html_path = OUTPUT_DIR / "disputeshield_architecture_1080p.html"
arch_png_path = OUTPUT_DIR / "disputeshield_architecture_1080p.png"
with open(arch_html_path, "w", encoding="utf-8") as f:
    f.write(architecture_html)

endcard_html_path = OUTPUT_DIR / "disputeshield_endcard_1080p.html"
endcard_png_path = OUTPUT_DIR / "disputeshield_endcard_1080p.png"
with open(endcard_html_path, "w", encoding="utf-8") as f:
    f.write(endcard_html)

thumb_html_path = OUTPUT_DIR / "disputeshield_thumbnail_1280x720.html"
thumb_png_path = OUTPUT_DIR / "disputeshield_thumbnail_1280x720.png"
with open(thumb_html_path, "w", encoding="utf-8") as f:
    f.write(thumbnail_html)

print("[1/3] HTML templates updated with exact project logo & dual-blue theme.")

# Render 1: Architecture Diagram (1920x1080)
subprocess.run([
    EDGE_BIN, "--headless", "--disable-gpu", "--hide-scrollbars",
    "--window-size=1920,1080",
    f"--screenshot={arch_png_path}",
    str(arch_html_path.resolve().as_uri())
], check=True, timeout=20)
print(f"[2/3] Rendered Architecture Diagram PNG: {arch_png_path}")

# Render 2: End Card (1920x1080)
subprocess.run([
    EDGE_BIN, "--headless", "--disable-gpu", "--hide-scrollbars",
    "--window-size=1920,1080",
    f"--screenshot={endcard_png_path}",
    str(endcard_html_path.resolve().as_uri())
], check=True, timeout=20)
print(f"[2/3] Rendered End Card PNG: {endcard_png_path}")

# Render 3: Thumbnail (1280x720)
subprocess.run([
    EDGE_BIN, "--headless", "--disable-gpu", "--hide-scrollbars",
    "--window-size=1280,720",
    f"--screenshot={thumb_png_path}",
    str(thumb_html_path.resolve().as_uri())
], check=True, timeout=20)
print(f"[3/3] Rendered Thumbnail PNG: {thumb_png_path}")
print("All broadcast graphics successfully updated!")
