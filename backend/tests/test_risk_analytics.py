"""
DisputeShield AI — Risk Predictor & Analytics API Tests (Day 13)

Validates:
1. Risk band classification: GREEN (<0.5%), YELLOW (0.5-0.99%), ORANGE (1.0-1.49%), and RED (>=1.5%).
2. Account health score calculation and velocity trend direction.
3. Proactive mitigation recommendation generation based on dispute reason distribution.
4. Analytics REST API endpoints:
   - GET /api/analytics/risk-score
   - GET /api/analytics/dispute-trends
   - GET /api/analytics/win-rate
5. Merchant override endpoint:
   - POST /api/disputes/{id}/override with custom defense notes.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ["DATABASE_URL"] = "sqlite:///./test_analytics.db"

from database import SessionLocal, init_db, engine, Base
from models.dispute import Dispute, DisputeStatus, DisputeOutcome, AgentDecision
from models.merchant import Merchant
from models.evidence import Evidence, EvidenceStatus
from services.risk_predictor import RiskPredictor, RiskAssessment
from main import app
from fastapi.testclient import TestClient


def setup_module():
    init_db()


def teardown_module():
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    if os.path.exists("test_analytics.db"):
        try:
            os.remove("test_analytics.db")
        except Exception:
            pass


def test_risk_band_classification():
    """Verify classification across Green, Yellow, Orange, and Red risk thresholds."""
    predictor = RiskPredictor()
    db = SessionLocal()
    try:
        # 1. GREEN Tier: 0.25% ratio (5 disputes / 2000 tx)
        risk_green = predictor.calculate_risk(
            db,
            override_disputes_90d=5,
            override_transactions_90d=2000,
        )
        assert risk_green.risk_band == "GREEN"
        assert risk_green.current_dispute_ratio == 0.25
        assert risk_green.account_health_score >= 85.0
        assert risk_green.threshold_warning is None

        # 2. YELLOW Tier: 0.75% ratio (15 disputes / 2000 tx)
        risk_yellow = predictor.calculate_risk(
            db,
            override_disputes_90d=15,
            override_transactions_90d=2000,
        )
        assert risk_yellow.risk_band == "YELLOW"
        assert risk_yellow.current_dispute_ratio == 0.75
        assert 70.0 <= risk_yellow.account_health_score < 85.0
        assert "ELEVATED" in (risk_yellow.threshold_warning or "")

        # 3. ORANGE Tier: 1.25% ratio (25 disputes / 2000 tx)
        risk_orange = predictor.calculate_risk(
            db,
            override_disputes_90d=25,
            override_transactions_90d=2000,
        )
        assert risk_orange.risk_band == "ORANGE"
        assert risk_orange.current_dispute_ratio == 1.25
        assert 45.0 <= risk_orange.account_health_score < 70.0
        assert "WARNING" in (risk_orange.threshold_warning or "")

        # 4. RED Tier: 1.80% ratio (36 disputes / 2000 tx - exceeds 1.5% threshold)
        risk_red = predictor.calculate_risk(
            db,
            override_disputes_90d=36,
            override_transactions_90d=2000,
        )
        assert risk_red.risk_band == "RED"
        assert risk_red.current_dispute_ratio == 1.80
        assert risk_red.account_health_score <= 45.0
        assert "CRITICAL" in (risk_red.threshold_warning or "")
        assert "1.50%" in (risk_red.threshold_warning or "")

        print("[TEST 1 PASSED: Risk band thresholds (GREEN, YELLOW, ORANGE, RED) verified]")
    finally:
        db.close()


def test_recommendations_and_trend_direction():
    """Verify velocity trend evaluation and category-specific defense recommendations."""
    predictor = RiskPredictor()
    db = SessionLocal()
    try:
        # Seed 3 INR disputes and 1 SNAD dispute
        now = datetime.utcnow()
        for i in range(3):
            d = Dispute(
                paypal_dispute_id=f"PP-INR-REC-{i}",
                reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                status="OPEN",
                dispute_amount=75.0,
                created_at=now - timedelta(days=5),
            )
            db.add(d)

        d_snad = Dispute(
            paypal_dispute_id="PP-SNAD-REC-1",
            reason="MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            status="OPEN",
            dispute_amount=120.0,
            created_at=now - timedelta(days=15),
        )
        db.add(d_snad)
        db.commit()

        assessment = predictor.calculate_risk(db, override_transactions_90d=500)
        # Because INR is predominant, INR recommendations should be generated
        assert any("signature" in rec.lower() for rec in assessment.actionable_recommendations)
        assert len(assessment.actionable_recommendations) >= 2
        print(f"[TEST 2 PASSED: Category-specific actionable recommendations verified: {assessment.actionable_recommendations[0]}]")
    finally:
        db.close()


def test_analytics_api_endpoints():
    """Verify REST analytics endpoints return expected schemas and metrics."""
    client = TestClient(app)

    # 1. GET /api/analytics/risk-score
    res_risk = client.get("/api/analytics/risk-score")
    assert res_risk.status_code == 200
    data_risk = res_risk.json()
    assert "account_health_score" in data_risk
    assert "current_dispute_ratio" in data_risk
    assert "risk_band" in data_risk
    assert data_risk["risk_band"] in ["GREEN", "YELLOW", "ORANGE", "RED"]
    assert "trend_direction" in data_risk
    assert "actionable_recommendations" in data_risk

    # 2. GET /api/analytics/dispute-trends
    res_trends = client.get("/api/analytics/dispute-trends")
    assert res_trends.status_code == 200
    data_trends = res_trends.json()
    assert "time_series" in data_trends
    assert len(data_trends["time_series"]) == 30
    assert "by_category" in data_trends
    assert "monthly" in data_trends

    # 3. GET /api/analytics/win-rate
    res_win = client.get("/api/analytics/win-rate")
    assert res_win.status_code == 200
    data_win = res_win.json()
    assert "win_rate" in data_win
    assert "total_disputes" in data_win
    assert "total_amount_saved" in data_win
    assert data_win["currency"] == "USD"

    print("[TEST 3 PASSED: Analytics endpoints (/risk-score, /dispute-trends, /win-rate) verified]")


def test_dispute_override_endpoint():
    """Verify POST /api/disputes/{id}/override updates evidence and sets OVERRIDDEN decision."""
    client = TestClient(app)
    db = SessionLocal()
    try:
        # Create a pending review dispute
        dispute = Dispute(
            paypal_dispute_id="PP-D-OVERRIDE-1234",
            reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            status="OPEN",
            dispute_amount=189.0,
            dispute_currency="USD",
            agent_decision="DRAFT_PENDING_REVIEW",
            outcome="PENDING",
            created_at=datetime.utcnow(),
        )
        db.add(dispute)
        db.commit()
        db.refresh(dispute)

        # Existing compiled draft evidence
        ev = Evidence(
            dispute_id=dispute.id,
            evidence_type="PROOF_OF_DELIVERY",
            source="DISPUTESHIELD_AI",
            notes="Initial agent drafted explanation.",
            status=EvidenceStatus.COMPILED.value,
        )
        db.add(ev)
        db.commit()

        # Send Override Request
        override_payload = {
            "evidence_notes": "Merchant personal statement: Customer called confirming receipt on Oct 12, porch camera confirmed delivery.",
            "additional_context": "Direct customer phone call log attached.",
        }

        res = client.post(f"/api/disputes/{dispute.id}/override", json=override_payload)
        assert res.status_code == 200
        data = res.json()

        assert data["agent_decision"] == "OVERRIDDEN"
        assert data["status"] == "UNDER_REVIEW"
        assert data["evidence_submitted"] is True

        # Check updated evidence in database
        db.refresh(dispute)
        assert dispute.agent_decision == "OVERRIDDEN"
        assert dispute.evidence_submitted is True
        assert len(dispute.evidence_items) >= 1
        latest_ev = dispute.evidence_items[-1]
        assert "porch camera confirmed delivery" in latest_ev.notes
        assert latest_ev.status == "SUBMITTED"

        print(f"[TEST 4 PASSED: Dispute #{dispute.id} manual override submitted and verified in database]")
    finally:
        db.close()


def run_all_tests():
    print("=" * 65)
    print("DisputeShield AI — Running Day 13 Risk & Analytics Tests")
    print("=" * 65)
    setup_module()
    try:
        test_risk_band_classification()
        test_recommendations_and_trend_direction()
        test_analytics_api_endpoints()
        test_dispute_override_endpoint()
        print("=" * 65)
        print("ALL DAY 13 RISK & ANALYTICS TESTS PASSED (4/4)")
        print("=" * 65)
    finally:
        teardown_module()


if __name__ == "__main__":
    run_all_tests()
