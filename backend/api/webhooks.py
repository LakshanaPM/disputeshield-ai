"""
DisputeShield AI — Webhook Receiver API

Receives PayPal webhook events, verifies signatures, stores events,
and enqueues them for async processing by the AI agent.
"""

import json
import logging
import time
import uuid
from datetime import datetime
from fastapi import APIRouter, Request, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from database import get_db
from models.webhook_event import WebhookEvent
from services.webhook_verifier import verify_paypal_webhook
from tasks.dispute_processor import process_dispute_webhook
from api.ws import broadcast_message

logger = logging.getLogger(__name__)

router = APIRouter(tags=["webhooks"])


@router.post("/paypal")
async def receive_paypal_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Receive and process PayPal webhook events.

    Flow:
    1. Parse the raw payload
    2. Verify webhook signature via verify_paypal_webhook
    3. Check idempotency (return already_processed if exists)
    4. Store raw event in database
    5. Enqueue Celery task (process_dispute_webhook)
    6. Return 200 within 200ms
    """
    try:
        body_bytes = await request.body()
        try:
            payload = json.loads(body_bytes)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON payload")

        event_id = payload.get("id", "")
        event_type = payload.get("event_type", "")
        if not event_id:
            raise HTTPException(status_code=400, detail="Missing event ID in webhook payload")

        logger.info(f"Webhook received: {event_type} (event_id: {event_id})")

        # --- Signature Verification ---
        headers = dict(request.headers)
        is_valid = await verify_paypal_webhook(headers=headers, event_body=payload)
        if not is_valid:
            logger.warning(f"Rejected webhook event {event_id}: Invalid signature.")
            raise HTTPException(status_code=400, detail="Invalid PayPal webhook signature")

        # --- Idempotency Check ---
        existing = db.query(WebhookEvent).filter(
            WebhookEvent.event_id == event_id
        ).first()

        if existing:
            logger.info(f"Duplicate webhook event {event_id}, already processed")
            return {"status": "already_processed", "event_id": event_id}

        # --- Store Raw Event ---
        resource = payload.get("resource") if isinstance(payload.get("resource"), dict) else {}
        resource_id = resource.get("dispute_id") or resource.get("id")

        create_time = None
        if payload.get("create_time"):
            try:
                create_time = datetime.fromisoformat(payload["create_time"].replace("Z", "+00:00"))
            except Exception:
                pass

        webhook_event = WebhookEvent(
            event_id=event_id,
            event_type=event_type,
            resource_type=payload.get("resource_type"),
            resource_id=resource_id,
            payload=body_bytes.decode("utf-8"),
            paypal_create_time=create_time,
        )
        db.add(webhook_event)
        db.commit()
        db.refresh(webhook_event)

        logger.info(f"Stored webhook event {event_id} (db_id: {webhook_event.id})")

        # --- Enqueue for Async Processing ---
        try:
            process_dispute_webhook.delay(webhook_event.id)
            logger.info(f"Dispatched Celery task process_dispute_webhook for event db_id={webhook_event.id}")
        except Exception as exc:
            logger.info(f"Celery broker unavailable, executing via in-process background task: {exc}")
            background_tasks.add_task(process_dispute_webhook, webhook_event.id)

        return {"status": "received", "event_id": event_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")


import time
import uuid
from typing import Optional
from pydantic import BaseModel
from api.ws import broadcast_message


SIMULATION_SCENARIOS = [
    {
        "name": "INR_DELIVERED",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "amount": "145.00",
        "currency": "USD",
        "buyer_name": "Marcus Vance",
        "buyer_email": "m.vance@example.com",
        "buyer_message": "Package was marked as delivered yesterday, but I checked my porch and mailbox and it is not there.",
        "carrier": "UPS",
        "tracking_number": "1Z9999999999999999",
        "delivery_status": "DELIVERED",
        "proof_of_delivery_available": True,
        "signature": "Signed by M. Vance",
        "description": "Item Not Received (Delivered with tracking proof) -> Auto-Submitted",
    },
    {
        "name": "SNAD_COLOR_DISCREPANCY",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "amount": "289.00",
        "currency": "USD",
        "buyer_name": "Elena Rostova",
        "buyer_email": "e.rostova@example.com",
        "buyer_message": "The item received is navy blue, but I ordered the midnight black variant. Packaging was opened.",
        "carrier": "FedEx",
        "tracking_number": "789456123000",
        "delivery_status": "DELIVERED",
        "proof_of_delivery_available": True,
        "signature": "Signed by E. Rostova",
        "description": "Significantly Not As Described -> Requires Merchant Review",
    },
    {
        "name": "INR_IN_TRANSIT_DELAY",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "amount": "199.50",
        "currency": "USD",
        "buyer_name": "David Sterling",
        "buyer_email": "d.sterling@example.com",
        "buyer_message": "Tracking stopped updating 5 days ago in transit due to severe weather. Delivery date has passed.",
        "carrier": "FedEx",
        "tracking_number": "456123789999",
        "delivery_status": "IN_TRANSIT",
        "proof_of_delivery_available": False,
        "signature": None,
        "description": "Item Not Received (In-Transit Delay) -> Requires Merchant Review",
    },
    {
        "name": "UNAUTHORIZED_TRANSACTION",
        "reason": "UNAUTHORIZED",
        "amount": "89.50",
        "currency": "USD",
        "buyer_name": "Chloe Bennett",
        "buyer_email": "c.bennett@example.com",
        "buyer_message": "I do not recognize this transaction on my PayPal statement. Please refund immediately.",
        "carrier": "USPS",
        "tracking_number": "9400111899562537123456",
        "delivery_status": "DELIVERED",
        "proof_of_delivery_available": True,
        "signature": None,
        "description": "Unauthorized Transaction (Fraud Telematics Verified) -> Auto-Submitted",
    },
]

_simulation_counter = 0


class SimulateWebhookRequest(BaseModel):
    reason: Optional[str] = None
    amount: Optional[str] = None
    currency: Optional[str] = None
    dispute_id: Optional[str] = None
    scenario_index: Optional[int] = None


def _process_simulation_async(event_id: int):
    try:
        process_dispute_webhook(event_id)
    except Exception as e:
        logger.warning(f"Error during inline simulation processing: {e}")


@router.post("/paypal/simulate")
async def simulate_paypal_webhook(
    req: SimulateWebhookRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Simulate incoming PayPal webhook for live hackathon demos.
    Rotates through realistic dispute scenarios to demonstrate both
    AUTO_SUBMITTED (hands-free) and DRAFT_PENDING_REVIEW (requires review).
    """
    global _simulation_counter
    try:
        # Determine scenario to use
        if req.scenario_index is not None and 0 <= req.scenario_index < len(SIMULATION_SCENARIOS):
            scenario = SIMULATION_SCENARIOS[req.scenario_index]
        else:
            scenario = SIMULATION_SCENARIOS[_simulation_counter % len(SIMULATION_SCENARIOS)]
            _simulation_counter += 1

        reason = req.reason or scenario["reason"]
        amount = req.amount or scenario["amount"]
        currency = req.currency or scenario["currency"]
        buyer_name = scenario["buyer_name"]
        buyer_email = scenario["buyer_email"]
        buyer_message = scenario["buyer_message"]

        dispute_num = int(time.time()) % 100000
        dispute_id = req.dispute_id or f"PP-D-{dispute_num}"
        event_id = f"WH-SIM-{uuid.uuid4().hex[:12].upper()}"
        now_iso = datetime.utcnow().isoformat() + "Z"

        payload = {
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
                    "value": str(amount),
                },
                "reason": reason,
                "status": "WAITING_FOR_SELLER_RESPONSE",
                "disputed_transactions": [
                    {
                        "seller_transaction_id": f"TXN-{uuid.uuid4().hex[:8].upper()}",
                        "invoice_number": f"INV-{int(time.time())}",
                    }
                ],
                "buyer": {
                    "name": buyer_name,
                    "email": buyer_email,
                },
                "messages": [
                    {
                        "posted_by": "BUYER",
                        "time_posted": now_iso,
                        "content": buyer_message,
                    }
                ],
            },
        }

        webhook_event = WebhookEvent(
            event_id=event_id,
            event_type="CUSTOMER.DISPUTE.CREATED",
            resource_type="dispute",
            resource_id=dispute_id,
            payload=json.dumps(payload),
            paypal_create_time=datetime.utcnow(),
        )
        db.add(webhook_event)
        db.commit()
        db.refresh(webhook_event)

        # Broadcast new dispute over WebSocket
        await broadcast_message({
            "type": "new_dispute",
            "dispute_id": dispute_id,
            "dispute_amount": float(amount),
            "reason": reason,
            "buyer_name": buyer_name,
            "buyer_message": buyer_message,
            "scenario": scenario["name"],
        })

        # Process Celery/dispute task asynchronously in background
        background_tasks.add_task(_process_simulation_async, webhook_event.id)

        return {
            "status": "simulated",
            "event_id": event_id,
            "dispute_id": dispute_id,
            "amount": amount,
            "reason": reason,
            "scenario": scenario["name"],
            "description": scenario["description"],
        }
    except Exception as exc:
        logger.error(f"Simulation error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))

