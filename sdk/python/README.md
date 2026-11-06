# disputeshield-sdk (Python)

Official Python SDK for **DisputeShield AI**, designed for merchant automation scripts, headless backend workflows, and APIMatic integration.

---

## 📦 Installation

```bash
pip install disputeshield-sdk
# or directly from repo
pip install -e sdk/python
```

---

## ⚡ Quickstart

```python
from disputeshield import DisputeShieldClient

# Initialize client
client = DisputeShieldClient(base_url="http://localhost:8000")

# 1. Fetch risk score & limitation velocity
risk = client.get_risk_score()
print(f"Current Dispute Ratio: {risk['current_dispute_ratio']}% ({risk['risk_band']})")

# 2. Query disputes requiring review
disputes = client.get_disputes(filter_tab="REVIEW_NEEDED")
print(f"Disputes Awaiting Sign-off: {disputes['total_count']}")

# 3. Simulate a new dispute webhook
sim = client.simulate_webhook(reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED", amount="145.00")
print(f"Simulated Ingested Dispute: {sim['dispute_id']}")
```

---

## 📄 License
MIT License

