# @disputeshield/sdk (TypeScript)

Official typed TypeScript client for **DisputeShield AI**, generated and formatted for modern Node.js and frontend environments via APIMatic.

---

## 📦 Installation

```bash
npm install @disputeshield/sdk
# or
yarn add @disputeshield/sdk
```

---

## ⚡ Quickstart

```typescript
import { DisputeShieldClient } from '@disputeshield/sdk';

// Initialize client
const client = new DisputeShieldClient({
  baseUrl: process.env.DISPUTESHIELD_API_URL || 'http://localhost:8000',
});

async function run() {
  // 1. Fetch live disputes for AG Grid Server-Side Row Model
  const disputes = await client.getDisputes({
    start_row: 0,
    end_row: 20,
    filter_tab: 'REVIEW_NEEDED',
  });
  console.log(`Requires Review: ${disputes.total_count} claims`);

  // 2. Fetch real-time PayPal 1.5% dispute velocity metrics
  const risk = await client.getRiskScore();
  console.log(`Current Dispute Ratio: ${risk.current_dispute_ratio}% (${risk.risk_band})`);

  // 3. Simulate an incoming PayPal dispute webhook event
  const simulation = await client.simulateWebhook({
    reason: 'MERCHANDISE_OR_SERVICE_NOT_RECEIVED',
    amount: '145.00',
  });
  console.log(`Simulated Ingested Dispute: ${simulation.dispute_id}`);
}

run().catch(console.error);
```

---

## 📄 License
MIT License

