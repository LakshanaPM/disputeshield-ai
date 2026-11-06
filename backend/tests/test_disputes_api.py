"""
DisputeShield AI — Disputes API Integration Tests

Validates:
1. AG Grid SSRM pagination, sorting, and filtering on GET /api/disputes.
2. Complete detail retrieval with relations on GET /api/disputes/{id}.
3. Merchant evidence approval and sandbox submission on POST /api/disputes/{id}/approve.
"""

import os
import sys
from datetime import datetime

os.environ["DATABASE_URL"] = "sqlite:///./test_disputes_api.db"
sys.path.insert(0, "backend")

from fastapi.testclient import TestClient
from main import app
from database import SessionLocal, init_db, engine, Base
from models import Dispute, Merchant, Evidence
from models.dispute import DisputeStatus, AgentDecision


def setup_module():
    init_db()


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_disputes_api.db"):
        try:
            os.remove("test_disputes_api.db")
        except Exception:
            pass


def test_disputes_api_flow():
    with TestClient(app) as client:
        db = SessionLocal()

        # Seed Merchant
        merchant = Merchant(
            paypal_merchant_id="MERCHANT-SANDBOX-01",
            business_name="DisputeShield Demo Store",
            account_health_score=88.5,
            dispute_ratio=0.8,
        )
        db.add(merchant)
        db.flush()

        # Seed Disputes
        d1 = Dispute(
            paypal_dispute_id="PP-DISPUTE-001",
            reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            status=DisputeStatus.OPEN.value,
            dispute_amount=75.0,
            dispute_currency="USD",
            merchant_id=merchant.id,
            agent_decision=AgentDecision.DRAFT_PENDING_REVIEW.value,
        )
        d2 = Dispute(
            paypal_dispute_id="PP-DISPUTE-002",
            reason="MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            status=DisputeStatus.UNDER_REVIEW.value,
            dispute_amount=199.99,
            dispute_currency="USD",
            merchant_id=merchant.id,
            agent_decision=AgentDecision.AUTO_SUBMITTED.value,
        )
        db.add_all([d1, d2])
        db.commit()

        # 1. Test AG Grid SSRM Listing
        res = client.get("/api/disputes?start_row=0&end_row=10&sort_col=dispute_amount&sort_dir=desc")
        assert res.status_code == 200, res.text
        data = res.json()
        assert "rows" in data
        assert data["total_count"] >= 2
        assert data["start_row"] == 0
        assert data["rows"][0]["dispute_amount"] >= data["rows"][1]["dispute_amount"]

        # 2. Test Filters
        res_filter = client.get("/api/disputes?reason=MERCHANDISE_OR_SERVICE_NOT_RECEIVED")
        assert res_filter.status_code == 200
        assert len(res_filter.json()["rows"]) == 1
        assert res_filter.json()["rows"][0]["paypal_dispute_id"] == "PP-DISPUTE-001"

        # 3. Test Detail View with Merchant & Evidence
        res_detail = client.get(f"/api/disputes/{d1.id}")
        assert res_detail.status_code == 200
        detail_data = res_detail.json()
        assert detail_data["paypal_dispute_id"] == "PP-DISPUTE-001"
        assert detail_data["merchant"] is not None
        assert detail_data["merchant"]["paypal_merchant_id"] == "MERCHANT-SANDBOX-01"

        # 4. Test Approval Action
        res_approve = client.post(
            f"/api/disputes/{d1.id}/approve",
            json={"approved": True, "modifications": "Carrier tracking shows delivered to porch on Oct 18."},
        )
        assert res_approve.status_code == 200, res_approve.text
        approved_data = res_approve.json()
        assert approved_data["agent_decision"] == "APPROVED"
        assert approved_data["status"] == DisputeStatus.UNDER_REVIEW.value
        assert approved_data["evidence_submitted"] is True
        assert len(approved_data["evidence_items"]) == 1
        assert "Carrier tracking shows delivered" in approved_data["evidence_items"][0]["notes"]

        db.close()
        print("\n[ALL DISPUTES API TESTS PASSED SUCCESSFULLY]")


if __name__ == "__main__":
    setup_module()
    test_disputes_api_flow()
    teardown_module()
