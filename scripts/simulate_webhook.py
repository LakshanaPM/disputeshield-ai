"""
DisputeShield AI — Webhook Simulation CLI

Fires simulated PayPal webhook notifications against the local or remote
DisputeShield API for testing the end-to-end ingestion and Celery pipeline.
"""

import argparse
import json
import time
import uuid
from datetime import datetime, timezone
import httpx


def generate_mock_dispute_payload(
    dispute_id: str,
    reason: str,
    amount: float,
    currency: str,
    buyer_email: str,
) -> dict:
    """Generate a realistic CUSTOMER.DISPUTE.CREATED webhook event body."""
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    event_id = f"WH-SIM-{uuid.uuid4().hex[:12].upper()}"

    return {
        "id": event_id,
        "event_version": "1.0",
        "create_time": now_iso,
        "resource_type": "dispute",
        "event_type": "CUSTOMER.DISPUTE.CREATED",
        "summary": f"Dispute created for {amount} {currency} due to {reason}",
        "resource": {
            "dispute_id": dispute_id,
            "create_time": now_iso,
            "update_time": now_iso,
            "dispute_life_cycle_stage": "INQUIRY",
            "dispute_state": "REQUIRED_ACTION",
            "dispute_amount": {
                "currency_code": currency,
                "value": f"{amount:.2f}",
            },
            "reason": reason,
            "status": "WAITING_FOR_SELLER_RESPONSE",
            "dispute_response_deadline": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "disputed_transactions": [
                {
                    "seller_transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
                    "invoice_number": f"INV-{int(time.time())}",
                }
            ],
            "buyer": {
                "name": "Jane Buyer",
                "email": buyer_email,
            },
            "messages": [
                {
                    "posted_by": "BUYER",
                    "time_posted": now_iso,
                    "content": "I ordered this product two weeks ago and tracking has not updated. Please issue a refund.",
                }
            ],
        },
    }


def main():
    parser = argparse.ArgumentParser(description="Simulate PayPal Webhooks against DisputeShield AI")
    parser.add_argument(
        "--url",
        default="http://localhost:8000/webhooks/paypal",
        help="Target webhook endpoint (default: http://localhost:8000/webhooks/paypal)",
    )
    parser.add_argument(
        "--reason",
        default="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        help="Dispute reason code (default: MERCHANDISE_OR_SERVICE_NOT_RECEIVED)",
    )
    parser.add_argument(
        "--amount",
        type=float,
        default=120.00,
        help="Dispute amount (default: 120.00)",
    )
    parser.add_argument(
        "--currency",
        default="USD",
        help="Currency code (default: USD)",
    )
    parser.add_argument(
        "--dispute-id",
        default=None,
        help="Custom dispute ID (default: auto-generated)",
    )
    parser.add_argument(
        "--buyer-email",
        default="buyer.demo@example.com",
        help="Buyer email (default: buyer.demo@example.com)",
    )

    args = parser.parse_args()

    dispute_id = args.dispute_id or f"PP-D-{int(time.time())}"
    payload = generate_mock_dispute_payload(
        dispute_id=dispute_id,
        reason=args.reason,
        amount=args.amount,
        currency=args.currency,
        buyer_email=args.buyer_email,
    )

    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    headers = {
        "PAYPAL-TRANSMISSION-ID": f"sim-tx-{uuid.uuid4()}",
        "PAYPAL-TRANSMISSION-TIME": now_iso,
        "PAYPAL-CERT-URL": "https://api.sandbox.paypal.com/v1/notifications/certs/CERT-360caa42-fca2a594-cce0ab68",
        "PAYPAL-AUTH-ALGO": "SHA256withRSA",
        "PAYPAL-TRANSMISSION-SIG": "MOCK_TRANSMISSION_SIG_SIMULATION",
        "Content-Type": "application/json",
    }

    print("=" * 65)
    print("DisputeShield AI — Webhook Simulation")
    print("=" * 65)
    print(f"Target URL:    {args.url}")
    print(f"Event ID:      {payload['id']}")
    print(f"Dispute ID:    {dispute_id}")
    print(f"Reason:        {args.reason}")
    print(f"Amount:        {args.amount:.2f} {args.currency}")
    print(f"Buyer:         {args.buyer_email}")
    print("-" * 65)

    start_time = time.time()
    try:
        response = httpx.post(args.url, json=payload, headers=headers, timeout=10.0)
        latency = (time.time() - start_time) * 1000

        print(f"Status Code:   {response.status_code}")
        print(f"Latency:       {latency:.1f}ms")
        print(f"Response Body: {response.text}")

        if response.status_code == 200:
            print("\n[SUCCESS] Webhook accepted by DisputeShield AI!")
        else:
            print(f"\n[FAILED] Server responded with error code {response.status_code}")

    except Exception as exc:
        print(f"\n[ERROR] Request failed: {exc}")
        print("Hint: Make sure the FastAPI backend is running (e.g. uvicorn main:app).")

    print("=" * 65)


if __name__ == "__main__":
    main()
