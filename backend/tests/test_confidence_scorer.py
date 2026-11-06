"""
DisputeShield AI — Confidence Scorer & End-to-End Pipeline Tests (Day 11)

Validates:
1. High-confidence dispute (Score >= 80, 0 gaps, submission_ready) -> AUTO_SUBMIT.
2. Moderate-confidence dispute (Score 60-79) -> DRAFT_PENDING_REVIEW.
3. Low-confidence dispute (Gaps, score < 60) -> ESCALATE_TO_HUMAN.
4. End-to-end execution of process_dispute_webhook Celery task verifying database persistence.
"""

import json
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_confidence.db"
sys.path.insert(0, "backend")

from database import SessionLocal, init_db, engine, Base
from models.dispute import Dispute, DisputeStatus, AgentDecision
from models.evidence import Evidence
from models.webhook_event import WebhookEvent
from agent.evidence_engine import EvidenceStrategyReport, CompiledEvidencePayload, EvidenceItem
from agent.confidence_scorer import ConfidenceScorer, ConfidenceDecision
from tasks.dispute_processor import process_dispute_webhook


def setup_module():
    init_db()


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_confidence.db"):
        try:
            os.remove("test_confidence.db")
        except Exception:
            pass


def test_high_confidence_auto_submit():
    scorer = ConfidenceScorer()
    strategy_report = EvidenceStrategyReport(
        dispute_id="PP-D-HIGH-1",
        category="INR",
        overall_strength_score=95.0,
        items=[],
        identified_gaps=[],
        recommended_action="Submit immediately",
        can_auto_submit=True,
    )
    compiled_payload = CompiledEvidencePayload(
        dispute_id="PP-D-HIGH-1",
        evidence_type="PROOF_OF_FULFILLMENT",
        notes="Carrier confirmed delivery.",
        tracking_info=[{"carrier_name": "UPS", "tracking_number": "1Z9999999999999999"}],
        submission_ready=True,
    )
    dispute_data = {"dispute_amount": 120.0}
    merchant_data = {"dispute_ratio": 0.4}

    decision = scorer.calculate_decision(strategy_report, compiled_payload, dispute_data, merchant_data)
    assert isinstance(decision, ConfidenceDecision)
    assert decision.confidence_score >= 80.0
    assert decision.decision == "AUTO_SUBMIT"
    print(f"[TEST 1 PASSED: High confidence scored {decision.confidence_score} -> AUTO_SUBMIT]")


def test_medium_confidence_draft_review():
    scorer = ConfidenceScorer()
    strategy_report = EvidenceStrategyReport(
        dispute_id="PP-D-MED-2",
        category="SNAD",
        overall_strength_score=68.0,
        items=[],
        identified_gaps=["Missing warehouse inspection photos."],
        recommended_action="Draft evidence for review",
        can_auto_submit=False,
    )
    compiled_payload = CompiledEvidencePayload(
        dispute_id="PP-D-MED-2",
        evidence_type="PROOF_OF_SIGNIFICANT_NOT_AS_DESCRIBED",
        notes="Product matches specification.",
        submission_ready=True,
    )
    dispute_data = {"dispute_amount": 250.0}
    merchant_data = {"dispute_ratio": 0.8}

    decision = scorer.calculate_decision(strategy_report, compiled_payload, dispute_data, merchant_data)
    assert isinstance(decision, ConfidenceDecision)
    assert 60.0 <= decision.confidence_score < 80.0
    assert decision.decision == "DRAFT_PENDING_REVIEW"
    print(f"[TEST 2 PASSED: Medium confidence scored {decision.confidence_score} -> DRAFT_PENDING_REVIEW]")


def test_low_confidence_escalate():
    scorer = ConfidenceScorer()
    strategy_report = EvidenceStrategyReport(
        dispute_id="PP-D-LOW-3",
        category="INR",
        overall_strength_score=35.0,
        items=[],
        identified_gaps=["Tracking shows package lost in transit."],
        recommended_action="Escalate to merchant team",
        can_auto_submit=False,
    )
    compiled_payload = CompiledEvidencePayload(
        dispute_id="PP-D-LOW-3",
        evidence_type="PROOF_OF_FULFILLMENT",
        notes="Incomplete fulfillment.",
        submission_ready=False,
    )
    dispute_data = {"dispute_amount": 450.0}
    merchant_data = {"dispute_ratio": 1.8}

    decision = scorer.calculate_decision(strategy_report, compiled_payload, dispute_data, merchant_data)
    assert isinstance(decision, ConfidenceDecision)
    assert decision.confidence_score < 60.0
    assert decision.decision == "ESCALATE_TO_HUMAN"
    print(f"[TEST 3 PASSED: Low confidence scored {decision.confidence_score} -> ESCALATE_TO_HUMAN]")


def test_end_to_end_celery_task_execution():
    db = SessionLocal()
    try:
        # Create a sample incoming webhook event
        sample_event = WebhookEvent(
            event_id="WH-TEST-E2E-001",
            event_type="CUSTOMER.DISPUTE.CREATED",
            resource_type="dispute",
            resource_id="PP-D-E2E-8899",
            payload=json.dumps({
                "id": "WH-TEST-E2E-001",
                "event_type": "CUSTOMER.DISPUTE.CREATED",
                "resource": {
                    "dispute_id": "PP-D-E2E-8899",
                    "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                    "status": "OPEN",
                    "dispute_amount": {"value": "125.00", "currency_code": "USD"},
                    "buyer_message": "Item was never received.",
                    "disputed_transactions": [{"seller_transaction_id": "TXN-8899"}],
                },
            }),
            processed=False,
        )
        db.add(sample_event)
        db.commit()
        event_id = sample_event.id

        # Run Celery processor synchronously
        res = process_dispute_webhook(event_id)
        assert res["status"] == "success"

        # Verify DB records created and updated
        dispute = db.query(Dispute).filter(Dispute.paypal_dispute_id == "PP-D-E2E-8899").first()
        assert dispute is not None
        assert dispute.dispute_amount == 125.0
        assert dispute.agent_decision in ["AUTO_SUBMITTED", "DRAFT_PENDING_REVIEW", "ESCALATED"]
        assert dispute.confidence_score is not None
        assert dispute.agent_reasoning is not None

        # Verify compiled evidence item
        evidence = db.query(Evidence).filter(Evidence.dispute_id == dispute.id).first()
        assert evidence is not None
        assert evidence.notes is not None
        assert evidence.status in ["SUBMITTED", "COMPILED", "PENDING"]
        print(f"[TEST 4 PASSED: End-to-end webhook processor created Dispute #{dispute.id} with decision '{dispute.agent_decision}']")

    finally:
        db.close()


def run_all_tests():
    print("=" * 60)
    print("DisputeShield AI — Running Day 11 Confidence Scorer Tests")
    print("=" * 60)

    setup_module()
    try:
        test_high_confidence_auto_submit()
        test_medium_confidence_draft_review()
        test_low_confidence_escalate()
        test_end_to_end_celery_task_execution()
        print("=" * 60)
        print("ALL DAY 11 CONFIDENCE SCORER TESTS PASSED SUCCESSFULLY (4/4)")
        print("=" * 60)
    finally:
        teardown_module()


if __name__ == "__main__":
    run_all_tests()
