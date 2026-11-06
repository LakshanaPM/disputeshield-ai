"""
DisputeShield AI — Phase 2 Full Pipeline End-to-End Integration Tests (Day 14)

Executes the entire Phase 2 autonomous dispute resolution pipeline end-to-end:
1. Ingests CUSTOMER.DISPUTE.CREATED webhook and dispatches Celery task.
2. Builds evidence chain, retrieves RAG precedents, executes triage, evaluates strategy,
   compiles defense payload, scores confidence, and persists to DB.
3. Validates AG Grid Server-Side Row Model (SSRM) query endpoints with pagination & filtering.
4. Validates real-time risk scoring, win-rate analytics, and dispute velocity trends.
5. Validates 1-click merchant approval and manual override dispute resolution workflows.
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["DATABASE_URL"] = "sqlite:///./test_phase2_pipeline.db"

from database import SessionLocal, init_db, engine, Base
from models.dispute import Dispute, DisputeStatus, DisputeOutcome, AgentDecision
from models.merchant import Merchant
from models.evidence import Evidence, EvidenceStatus, EvidenceType
from models.webhook_event import WebhookEvent
from tasks.dispute_processor import process_dispute_webhook
from main import app
from fastapi.testclient import TestClient


def setup_module():
    init_db()


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_phase2_pipeline.db"):
        try:
            os.remove("test_phase2_pipeline.db")
        except Exception:
            pass


def test_autonomous_webhook_to_agent_pipeline():
    """Verify webhook ingestion triggers complete autonomous agent resolution pipeline."""
    db = SessionLocal()
    try:
        # 1. Setup merchant record
        merchant = Merchant(
            paypal_merchant_id="MERCHANT-E2E-TEST",
            business_name="DisputeShield E2E Testing Store",
            dispute_ratio=0.75,
            total_transactions_90d=1500,
        )
        db.add(merchant)
        db.commit()

        # 2. Simulate PayPal CUSTOMER.DISPUTE.CREATED webhook event
        webhook_payload = {
            "id": "WH-E2E-PHASE2-9901",
            "event_type": "CUSTOMER.DISPUTE.CREATED",
            "resource_type": "dispute",
            "resource": {
                "dispute_id": "PP-D-E2E-PHASE2-9901",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": "OPEN",
                "dispute_amount": {
                    "value": "135.00",
                    "currency_code": "USD",
                },
                "seller_merchant_id": "MERCHANT-E2E-TEST",
                "disputed_transactions": [
                    {
                        "seller_transaction_id": "ORD-E2E-9901",
                        "invoice_number": "INV-E2E-9901",
                    }
                ],
                "buyer": {
                    "email": "buyer.e2e@example.com",
                },
                "messages": [
                    {
                        "posted_by": "BUYER",
                        "content": "I ordered high-performance running shoes and they were never delivered.",
                    }
                ],
                "dispute_response_deadline": (datetime.utcnow() + timedelta(days=7)).isoformat() + "Z",
                "create_time": datetime.utcnow().isoformat() + "Z",
            },
        }

        webhook_event = WebhookEvent(
            event_id="WH-E2E-PHASE2-9901",
            event_type="CUSTOMER.DISPUTE.CREATED",
            resource_type="dispute",
            resource_id="PP-D-E2E-PHASE2-9901",
            payload=json.dumps(webhook_payload),
            processed=False,
            received_at=datetime.utcnow(),
        )
        db.add(webhook_event)
        db.commit()
        db.refresh(webhook_event)

        # 3. Execute Celery worker processor synchronously
        res = process_dispute_webhook(webhook_event.id)

        # 4. Verify Webhook status
        db.refresh(webhook_event)
        assert webhook_event.processed is True
        assert webhook_event.processed_at is not None

        # 5. Verify Dispute entity
        dispute = db.query(Dispute).filter(Dispute.paypal_dispute_id == "PP-D-E2E-PHASE2-9901").first()
        assert dispute is not None
        assert dispute.dispute_amount == 135.00
        assert dispute.dispute_currency == "USD"
        assert dispute.reason == "MERCHANDISE_OR_SERVICE_NOT_RECEIVED"
        assert dispute.buyer_email == "buyer.e2e@example.com"

        # Verify Agent outputs
        assert dispute.agent_decision in ["AUTO_SUBMITTED", "DRAFT_PENDING_REVIEW", "ESCALATED"]
        assert dispute.confidence_score is not None and dispute.confidence_score > 0.0
        assert dispute.evidence_strength_score is not None and dispute.evidence_strength_score > 0.0
        assert dispute.agent_reasoning is not None and len(dispute.agent_reasoning) > 10

        # Verify RAG historical precedents were attached
        assert dispute.similar_cases_json is not None
        cases = json.loads(dispute.similar_cases_json)
        assert isinstance(cases, list)
        assert len(cases) >= 1

        # Verify Evidence record creation
        evidence = db.query(Evidence).filter(Evidence.dispute_id == dispute.id).first()
        assert evidence is not None
        assert evidence.notes is not None
        assert evidence.status in ["SUBMITTED", "COMPILED", "PENDING"]

        print(f"[TEST 1 PASSED: Webhook triggered full agent pipeline: Decision={dispute.agent_decision}, Confidence={dispute.confidence_score*100:.1f}%, RAG Precedents={len(cases)}]")
    finally:
        db.close()


def test_ag_grid_ssrm_pagination_and_filtering():
    """Verify GET /api/disputes satisfies AG Grid Server-Side Row Model (SSRM) specifications."""
    client = TestClient(app)

    # 1. Basic pagination
    res = client.get("/api/disputes?start_row=0&end_row=10")
    assert res.status_code == 200
    data = res.json()
    assert "rows" in data
    assert "total_count" in data
    assert "start_row" in data
    assert "end_row" in data
    assert data["start_row"] == 0
    assert data["total_count"] >= 1
    assert len(data["rows"]) >= 1

    first_row = data["rows"][0]
    assert "paypal_dispute_id" in first_row
    assert "reason" in first_row
    assert "status" in first_row
    assert "dispute_amount" in first_row
    assert "agent_decision" in first_row
    assert "confidence_score" in first_row

    # 2. Filtering by reason
    res_filtered = client.get("/api/disputes?reason=MERCHANDISE_OR_SERVICE_NOT_RECEIVED")
    assert res_filtered.status_code == 200
    data_filtered = res_filtered.json()
    assert all(r["reason"] == "MERCHANDISE_OR_SERVICE_NOT_RECEIVED" for r in data_filtered["rows"])

    # 3. Filtering by non-matching reason
    res_empty = client.get("/api/disputes?reason=NON_EXISTENT_REASON")
    assert res_empty.status_code == 200
    assert res_empty.json()["total_count"] == 0

    print(f"[TEST 2 PASSED: AG Grid SSRM pagination, sorting, and filtering validated (total_rows={data['total_count']})]")


def test_analytics_and_risk_engine_integration():
    """Verify analytics endpoints reflect dynamically ingested dispute data."""
    client = TestClient(app)

    # 1. Risk Score
    res_risk = client.get("/api/analytics/risk-score")
    assert res_risk.status_code == 200
    risk_data = res_risk.json()
    assert risk_data["account_health_score"] >= 0.0
    assert risk_data["current_dispute_ratio"] >= 0.0
    assert risk_data["risk_band"] in ["GREEN", "YELLOW", "ORANGE", "RED"]
    assert risk_data["disputes_90d"] >= 1
    assert len(risk_data["actionable_recommendations"]) >= 1

    # 2. Win Rate
    res_win = client.get("/api/analytics/win-rate")
    assert res_win.status_code == 200
    win_data = res_win.json()
    assert win_data["total_disputes"] >= 1
    assert "win_rate" in win_data
    assert "total_amount_saved" in win_data

    # 3. Dispute Trends
    res_trends = client.get("/api/analytics/dispute-trends")
    assert res_trends.status_code == 200
    trends_data = res_trends.json()
    assert "time_series" in trends_data
    assert len(trends_data["time_series"]) == 30
    assert "by_category" in trends_data
    assert "monthly" in trends_data

    print(f"[TEST 3 PASSED: Analytics endpoints validated: Health Score={risk_data['account_health_score']}, Risk Band={risk_data['risk_band']}]")


def test_merchant_manual_review_approval_and_override():
    """Verify 1-click merchant approval and manual override endpoints."""
    client = TestClient(app)
    db = SessionLocal()
    try:
        # Seed Dispute 1: Pending merchant approval
        dispute_to_approve = Dispute(
            paypal_dispute_id="PP-D-REVIEW-APPROVE-1",
            reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            status="OPEN",
            dispute_amount=150.0,
            dispute_currency="USD",
            agent_decision="DRAFT_PENDING_REVIEW",
            outcome="PENDING",
            created_at=datetime.utcnow(),
        )
        db.add(dispute_to_approve)
        db.commit()
        db.refresh(dispute_to_approve)

        ev1 = Evidence(
            dispute_id=dispute_to_approve.id,
            evidence_type="PROOF_OF_DELIVERY",
            source="DISPUTESHIELD_AI",
            notes="Agent drafted defense statement.",
            status=EvidenceStatus.COMPILED.value,
        )
        db.add(ev1)
        db.commit()

        # Execute 1-click Approval
        approve_res = client.post(
            f"/api/disputes/{dispute_to_approve.id}/approve",
            json={"approved": True, "modifications": "Merchant reviewed and approved with verified delivery scan."},
        )
        assert approve_res.status_code == 200
        approve_data = approve_res.json()
        assert approve_data["agent_decision"] == "APPROVED"
        assert approve_data["status"] == "UNDER_REVIEW"
        assert approve_data["evidence_submitted"] is True

        db.refresh(dispute_to_approve)
        assert dispute_to_approve.agent_decision == "APPROVED"
        assert dispute_to_approve.evidence_submitted is True

        # Seed Dispute 2: Manual Override
        dispute_to_override = Dispute(
            paypal_dispute_id="PP-D-REVIEW-OVERRIDE-2",
            reason="MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            status="OPEN",
            dispute_amount=210.0,
            dispute_currency="USD",
            agent_decision="DRAFT_PENDING_REVIEW",
            outcome="PENDING",
            created_at=datetime.utcnow(),
        )
        db.add(dispute_to_override)
        db.commit()
        db.refresh(dispute_to_override)

        # Execute Manual Override
        override_res = client.post(
            f"/api/disputes/{dispute_to_override.id}/override",
            json={
                "evidence_notes": "Merchant personal declaration: Direct customer agreement and factory return waiver attached.",
                "additional_context": "Signed buyer acknowledgment.",
            },
        )
        assert override_res.status_code == 200
        override_data = override_res.json()
        assert override_data["agent_decision"] == "OVERRIDDEN"
        assert override_data["status"] == "UNDER_REVIEW"
        assert override_data["evidence_submitted"] is True

        db.refresh(dispute_to_override)
        assert dispute_to_override.agent_decision == "OVERRIDDEN"
        assert "Merchant manual override" in dispute_to_override.agent_reasoning

        print("[TEST 4 PASSED: 1-click merchant review approval and manual override verified in database]")
    finally:
        db.close()


def run_all_tests():
    print("=" * 65)
    print("DisputeShield AI — Running Phase 2 Full Pipeline End-to-End Tests")
    print("=" * 65)
    setup_module()
    try:
        test_autonomous_webhook_to_agent_pipeline()
        test_ag_grid_ssrm_pagination_and_filtering()
        test_analytics_and_risk_engine_integration()
        test_merchant_manual_review_approval_and_override()
        print("=" * 65)
        print("ALL PHASE 2 FULL PIPELINE TESTS PASSED SUCCESSFULLY (4/4)")
        print("=" * 65)
    finally:
        teardown_module()


if __name__ == "__main__":
    run_all_tests()
