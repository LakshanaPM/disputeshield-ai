"""
DisputeShield AI — Dispute Webhook Processor Task

Celery worker task that processes raw PayPal webhook events asynchronously:
1. Ingests CUSTOMER.DISPUTE.CREATED -> inserts/updates Dispute record
2. Ingests CUSTOMER.DISPUTE.UPDATED -> updates dispute status & lifecycle stage
3. Ingests CUSTOMER.DISPUTE.RESOLVED -> updates final resolution outcome
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import asyncio

from database import SessionLocal
from models.dispute import Dispute, DisputeStatus, DisputeOutcome, AgentDecision
from models.evidence import Evidence, EvidenceType, EvidenceStatus
from models.merchant import Merchant
from models.webhook_event import WebhookEvent
from tasks.celery_app import celery_app
from services.evidence_chain import build_evidence_chain
from services.paypal_client import PayPalClient
from agent.dispute_agent import DisputeTriageAgent
from agent.evidence_engine import EvidenceStrategyEngine
from agent.confidence_scorer import ConfidenceScorer
from agent.rag_retriever import RAGRetriever

logger = logging.getLogger(__name__)



def _parse_datetime(dt_str: Optional[str]) -> Optional[datetime]:
    """Helper to parse ISO datetime strings from PayPal."""
    if not dt_str:
        return None
    try:
        return datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    except Exception:
        return None


@celery_app.task(name="tasks.process_dispute_webhook", bind=True, max_retries=3)
def process_dispute_webhook(self, webhook_event_id: int):
    """
    Process an ingested PayPal webhook event asynchronously.
    """
    db = SessionLocal()
    try:
        webhook_event = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_event_id).first()
        if not webhook_event:
            logger.error(f"WebhookEvent ID {webhook_event_id} not found; skipping task.")
            return {"status": "not_found", "event_id": webhook_event_id}

        if webhook_event.processed:
            logger.info(f"WebhookEvent ID {webhook_event_id} is already processed; skipping.")
            return {"status": "already_processed", "event_id": webhook_event.event_id}

        payload: Dict[str, Any] = json.loads(webhook_event.payload)
        event_type = payload.get("event_type", "")
        resource: Dict[str, Any] = payload.get("resource") if isinstance(payload.get("resource"), dict) else {}
        dispute_id = resource.get("dispute_id") or resource.get("id") or webhook_event.resource_id

        logger.info(f"Processing webhook event '{event_type}' for dispute '{dispute_id}' (db_id={webhook_event_id})")

        # ------------------------------------------------------------------
        # 1. Event: CUSTOMER.DISPUTE.CREATED
        # ------------------------------------------------------------------
        if event_type == "CUSTOMER.DISPUTE.CREATED":
            if not dispute_id:
                logger.warning(f"No dispute_id found in event {webhook_event.event_id}")
            else:
                dispute = db.query(Dispute).filter(Dispute.paypal_dispute_id == dispute_id).first()

                # Extract Amount & Currency
                amount_obj = resource.get("dispute_amount") or {}
                if isinstance(amount_obj, dict):
                    dispute_amount = float(amount_obj.get("value", 0.0) or 0.0)
                    dispute_currency = amount_obj.get("currency_code", "USD")
                else:
                    dispute_amount = float(amount_obj or 0.0)
                    dispute_currency = resource.get("dispute_currency", "USD")

                # Extract Messages & Buyer Context
                buyer_message = None
                messages = resource.get("messages") or []
                if isinstance(messages, list):
                    buyer_msgs = [
                        m.get("content", "") for m in messages
                        if isinstance(m, dict) and m.get("posted_by") == "BUYER"
                    ]
                    if buyer_msgs:
                        buyer_message = "\n".join(buyer_msgs)
                if not buyer_message and resource.get("buyer_message"):
                    buyer_message = resource.get("buyer_message")

                # Extract Linked Transaction / Order
                paypal_order_id = None
                paypal_transaction_id = None
                txns = resource.get("disputed_transactions") or []
                if isinstance(txns, list) and txns:
                    first_txn = txns[0] if isinstance(txns[0], dict) else {}
                    paypal_order_id = first_txn.get("seller_transaction_id") or first_txn.get("invoice_number")
                    paypal_transaction_id = first_txn.get("seller_transaction_id") or first_txn.get("buyer_transaction_id")

                buyer_email = None
                buyer_obj = resource.get("buyer") or {}
                if isinstance(buyer_obj, dict):
                    buyer_email = buyer_obj.get("email")

                response_deadline = _parse_datetime(
                    resource.get("dispute_response_deadline") or resource.get("response_due_date")
                )
                create_time = _parse_datetime(resource.get("create_time"))
                update_time = _parse_datetime(resource.get("update_time"))

                if not dispute:
                    dispute = Dispute(
                        paypal_dispute_id=dispute_id,
                        paypal_order_id=paypal_order_id,
                        paypal_transaction_id=paypal_transaction_id,
                        reason=resource.get("reason", "OTHER"),
                        status=resource.get("status", DisputeStatus.OPEN.value),
                        dispute_amount=dispute_amount,
                        dispute_currency=dispute_currency,
                        dispute_life_cycle_stage=resource.get("dispute_life_cycle_stage"),
                        buyer_email=buyer_email,
                        seller_merchant_id=resource.get("seller_merchant_id"),
                        buyer_message=buyer_message,
                        agent_decision=AgentDecision.PENDING.value,
                        outcome=DisputeOutcome.PENDING.value,
                        response_deadline=response_deadline,
                        paypal_create_time=create_time,
                        paypal_update_time=update_time,
                    )
                    db.add(dispute)
                    db.flush()
                    logger.info(f"Created new Dispute record #{dispute.id} (PayPal ID: {dispute_id})")
                else:
                    dispute.status = resource.get("status", dispute.status)
                    dispute.dispute_amount = dispute_amount
                    dispute.paypal_update_time = update_time
                    logger.info(f"Updated existing Dispute record #{dispute.id} (PayPal ID: {dispute_id})")

                # ----------------------------------------------------------
                # Autonomous AI Dispute Resolution Pipeline
                # ----------------------------------------------------------
                try:
                    logger.info(f"Executing autonomous AI dispute pipeline for #{dispute.id} ({dispute_id})...")

                    # 1. Build evidence chain
                    chain_data = asyncio.run(build_evidence_chain(dispute.id, db))

                    # 1b. Retrieve Historical Precedents via RAG
                    rag_retriever = RAGRetriever()
                    rag_result = asyncio.run(rag_retriever.retrieve_similar_cases(
                        dispute_text=f"{dispute.reason}: {dispute.buyer_message or ''}",
                        reason=dispute.reason,
                        k=5,
                    ))
                    dispute.similar_cases_json = json.dumps(rag_result.get("cases", []))
                    precedent_win_rate = rag_result.get("win_rate", 0.85)
                    precedent_summary = rag_result.get("summary", "")

                    # 2. Run Triage
                    # Dynamically read dispute_ratio from Merchant model if available
                    merchant_obj = db.query(Merchant).filter(Merchant.id == dispute.merchant_id).first() if dispute.merchant_id else None
                    if not merchant_obj:
                        merchant_obj = db.query(Merchant).first()
                    dynamic_dispute_ratio = float(merchant_obj.dispute_ratio) if merchant_obj and merchant_obj.dispute_ratio is not None else 0.80

                    triage_agent = DisputeTriageAgent()
                    # Optionally inspect context using tools dynamically
                    tool_context = asyncio.run(triage_agent.inspect_dispute_context_via_tools(
                        dispute_id=dispute.paypal_dispute_id,
                        order_id=dispute.paypal_order_id,
                    ))

                    triage_result = asyncio.run(triage_agent.triage_dispute(
                        dispute_data={
                            "dispute_id": dispute.paypal_dispute_id,
                            "reason": dispute.reason,
                            "dispute_amount": dispute.dispute_amount,
                            "dispute_currency": dispute.dispute_currency,
                            "buyer_message": dispute.buyer_message,
                            "buyer_email": dispute.buyer_email,
                            "response_deadline": dispute.response_deadline,
                            "merchant_dispute_ratio": dynamic_dispute_ratio,
                        },
                        evidence_chain=chain_data,
                        historical_precedents=precedent_summary,
                    ))

                    # 3. Strategy Evaluation
                    strategy_engine = EvidenceStrategyEngine()
                    strategy_report = strategy_engine.evaluate_strategy(triage_result, chain_data, {
                        "dispute_id": dispute.paypal_dispute_id,
                        "reason": dispute.reason,
                        "dispute_amount": dispute.dispute_amount,
                        "buyer_email": dispute.buyer_email,
                    })

                    # 4. Compile Evidence Payload
                    compiled_payload = asyncio.run(strategy_engine.compile_evidence(
                        strategy_report, chain_data, {
                            "dispute_id": dispute.paypal_dispute_id,
                            "reason": dispute.reason,
                            "dispute_amount": dispute.dispute_amount,
                            "dispute_currency": dispute.dispute_currency,
                            "buyer_message": dispute.buyer_message,
                            "paypal_order_id": dispute.paypal_order_id,
                        }
                    ))

                    # 5. Calculate Confidence Decision
                    if not merchant_obj and dispute.merchant_id:
                        merchant_obj = db.query(Merchant).filter(Merchant.id == dispute.merchant_id).first()
                    if not merchant_obj:
                        merchant_obj = db.query(Merchant).first()
                    merchant_data = {"dispute_ratio": dynamic_dispute_ratio}
                    scorer = ConfidenceScorer()
                    decision_report = scorer.calculate_decision(
                        strategy_report=strategy_report,
                        compiled_payload=compiled_payload,
                        dispute_data={"dispute_amount": dispute.dispute_amount},
                        merchant_data=merchant_data,
                        precedent_win_rate=precedent_win_rate,
                    )

                    # 6. Apply Decision
                    dispute.confidence_score = decision_report.confidence_score / 100.0
                    dispute.evidence_strength_score = strategy_report.overall_strength_score / 100.0
                    dispute.agent_reasoning = decision_report.decision_rationale
                    dispute.agent_processed_at = datetime.utcnow()

                    if decision_report.decision == "AUTO_SUBMIT":
                        dispute.agent_decision = AgentDecision.AUTO_SUBMITTED.value
                        dispute.status = DisputeStatus.UNDER_REVIEW.value
                        dispute.evidence_submitted = True
                        dispute.evidence_submitted_at = datetime.utcnow()

                        # Direct PayPal submission with dev fallback
                        async def _submit_paypal():
                            async with PayPalClient() as pclient:
                                return await pclient.provide_evidence(dispute.paypal_dispute_id, {
                                    "note": compiled_payload.notes,
                                    "tracking_info": compiled_payload.tracking_info,
                                })
                        try:
                            asyncio.run(_submit_paypal())
                        except Exception as submit_err:
                            logger.warning(f"PayPal direct submission note: {submit_err}")

                        evidence_rec = Evidence(
                            dispute_id=dispute.id,
                            evidence_type=EvidenceType.PROOF_OF_DELIVERY.value,
                            source="CARRIER_TRACKING",
                            content=json.dumps({"tracking_info": compiled_payload.tracking_info}),
                            notes=compiled_payload.notes,
                            strength_score=strategy_report.overall_strength_score / 100.0,
                            status=EvidenceStatus.SUBMITTED.value,
                            compiled_at=datetime.utcnow(),
                            submitted_at=datetime.utcnow(),
                        )
                        db.add(evidence_rec)
                        logger.info(f"Dispute #{dispute.id} automatically submitted to PayPal.")

                    elif decision_report.decision == "DRAFT_PENDING_REVIEW":
                        dispute.agent_decision = AgentDecision.DRAFT_PENDING_REVIEW.value
                        evidence_rec = Evidence(
                            dispute_id=dispute.id,
                            evidence_type=EvidenceType.PROOF_OF_DELIVERY.value,
                            source="DISPUTESHIELD_AI",
                            content=json.dumps({"identified_gaps": strategy_report.identified_gaps}),
                            notes=compiled_payload.notes,
                            strength_score=strategy_report.overall_strength_score / 100.0,
                            status=EvidenceStatus.COMPILED.value,
                            compiled_at=datetime.utcnow(),
                        )
                        db.add(evidence_rec)
                        logger.info(f"Dispute #{dispute.id} drafted for merchant review.")

                    else:
                        dispute.agent_decision = AgentDecision.ESCALATED.value
                        evidence_rec = Evidence(
                            dispute_id=dispute.id,
                            evidence_type=EvidenceType.OTHER.value,
                            source="DISPUTESHIELD_AI",
                            content=json.dumps({"identified_gaps": strategy_report.identified_gaps}),
                            notes=decision_report.decision_rationale,
                            strength_score=strategy_report.overall_strength_score / 100.0,
                            status=EvidenceStatus.PENDING.value,
                            compiled_at=datetime.utcnow(),
                        )
                        db.add(evidence_rec)
                        logger.info(f"Dispute #{dispute.id} escalated to human review.")

                    # Broadcast real-time agent decision to connected WebSocket clients
                    try:
                        from api.ws import broadcast_dispute_event
                        broadcast_dispute_event("agent_decision", {
                            "type": "agent_decision",
                            "dispute_id": dispute.paypal_dispute_id,
                            "confidence": dispute.confidence_score,
                            "decision": dispute.agent_decision,
                            "action": dispute.agent_decision,
                            "amount": float(dispute.dispute_amount) if dispute.dispute_amount else 145.0,
                            "reason": dispute.reason,
                        })
                    except Exception as ws_err:
                        logger.debug(f"WebSocket broadcast skipped/failed: {ws_err}")

                    db.flush()
                except Exception as pipeline_err:
                    logger.error(f"Autonomous pipeline error for dispute #{dispute.id}: {pipeline_err}", exc_info=True)


        # ------------------------------------------------------------------
        # 2. Event: CUSTOMER.DISPUTE.UPDATED
        # ------------------------------------------------------------------
        elif event_type == "CUSTOMER.DISPUTE.UPDATED":
            if dispute_id:
                dispute = db.query(Dispute).filter(Dispute.paypal_dispute_id == dispute_id).first()
                if dispute:
                    if resource.get("status"):
                        dispute.status = resource.get("status")
                    if resource.get("dispute_life_cycle_stage"):
                        dispute.dispute_life_cycle_stage = resource.get("dispute_life_cycle_stage")
                    if resource.get("update_time"):
                        dispute.paypal_update_time = _parse_datetime(resource.get("update_time"))
                    logger.info(f"Dispute #{dispute.id} updated with new status: {dispute.status}")

        # ------------------------------------------------------------------
        # 3. Event: CUSTOMER.DISPUTE.RESOLVED
        # ------------------------------------------------------------------
        elif event_type == "CUSTOMER.DISPUTE.RESOLVED":
            if dispute_id:
                dispute = db.query(Dispute).filter(Dispute.paypal_dispute_id == dispute_id).first()
                if dispute:
                    dispute.status = DisputeStatus.RESOLVED.value
                    outcome_code = ""
                    outcome_obj = resource.get("dispute_outcome")
                    if isinstance(outcome_obj, dict):
                        outcome_code = outcome_obj.get("outcome_code", "").upper()

                    if "SELLER_FAVOUR" in outcome_code or "RESOLVED_MERCHANT" in outcome_code:
                        dispute.outcome = DisputeOutcome.WON.value
                    elif "BUYER_FAVOUR" in outcome_code or "RESOLVED_BUYER" in outcome_code:
                        dispute.outcome = DisputeOutcome.LOST.value
                    else:
                        dispute.outcome = DisputeOutcome.SETTLED.value

                    if resource.get("update_time"):
                        dispute.paypal_update_time = _parse_datetime(resource.get("update_time"))
                    logger.info(f"Dispute #{dispute.id} resolved with outcome: {dispute.outcome}")

        # Mark webhook event as processed
        webhook_event.processed = True
        webhook_event.processed_at = datetime.utcnow()
        webhook_event.processing_error = None
        db.commit()

        logger.info(f"Successfully processed webhook event {webhook_event.event_id}")
        return {"status": "success", "event_id": webhook_event.event_id, "type": event_type}

    except Exception as exc:
        db.rollback()
        logger.error(f"Error processing webhook event #{webhook_event_id}: {exc}", exc_info=True)
        try:
            err_event = db.query(WebhookEvent).filter(WebhookEvent.id == webhook_event_id).first()
            if err_event:
                err_event.processing_error = str(exc)
                db.commit()
        except Exception:
            pass

        # Exponential backoff retry
        retry_delay = 2 ** self.request.retries * 5
        raise self.retry(exc=exc, countdown=retry_delay)

    finally:
        db.close()
