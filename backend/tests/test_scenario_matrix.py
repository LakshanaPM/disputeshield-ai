"""
DisputeShield AI — 10-Scenario Dispute Decision Matrix & Pipeline Integration Test (Day 21)

Executes 10 distinct, realistic dispute scenarios through the agent triage,
evidence strategy, and confidence scoring engines:
1. Physical INR Delivered with UPS tracking -> AUTO_SUBMIT
2. Physical INR In-Transit weather delay -> DRAFT_PENDING_REVIEW
3. Physical INR Untracked economy post -> ESCALATE_TO_HUMAN
4. Digital Goods INR with server access log -> AUTO_SUBMIT
5. Digital Goods INR with failed download -> DRAFT_PENDING_REVIEW
6. SNAD with catalog SKU match -> DRAFT_PENDING_REVIEW
7. SNAD with warehouse packing error -> ESCALATE_TO_HUMAN
8. Unauthorized charge with verified address match -> AUTO_SUBMIT
9. Unauthorized charge with unauthorized freight reroute -> ESCALATE_TO_HUMAN
10. High-Value claim ($850) missing signature receipt -> DRAFT_PENDING_REVIEW
"""

import sys
from pathlib import Path
from typing import Dict, Any, List

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from agent.evidence_engine import EvidenceStrategyReport, CompiledEvidencePayload
from agent.confidence_scorer import ConfidenceScorer, ConfidenceDecision
from database import Base, engine, SessionLocal
from models.dispute import Dispute, DisputeStatus, DisputeOutcome, AgentDecision
from models.evidence import Evidence, EvidenceType, EvidenceStatus


def get_scenario_definitions() -> List[Dict[str, Any]]:
    return [
        {
            "id": 1,
            "name": "Physical INR Delivered with UPS tracking",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 89.00,
            "overall_strength_score": 95.0,
            "identified_gaps": [],
            "submission_ready": True,
            "precedent_win_rate": 0.90,
            "merchant_ratio": 0.4,
            "expected_decision": "AUTO_SUBMIT",
            "min_score": 80.0,
            "max_score": 100.0,
        },
        {
            "id": 2,
            "name": "Physical INR In-Transit weather delay",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 120.00,
            "overall_strength_score": 65.0,
            "identified_gaps": ["Carrier package in transit with weather delay exception"],
            "submission_ready": True,
            "precedent_win_rate": 0.70,
            "merchant_ratio": 0.6,
            "expected_decision": "DRAFT_PENDING_REVIEW",
            "min_score": 60.0,
            "max_score": 79.9,
        },
        {
            "id": 3,
            "name": "Physical INR Untracked economy post",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 45.00,
            "overall_strength_score": 30.0,
            "identified_gaps": ["No carrier tracking number or postal proof of delivery"],
            "submission_ready": False,
            "precedent_win_rate": 0.40,
            "merchant_ratio": 1.2,
            "expected_decision": "ESCALATE_TO_HUMAN",
            "min_score": 0.0,
            "max_score": 59.9,
        },
        {
            "id": 4,
            "name": "Digital Goods INR with server access log",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 49.00,
            "overall_strength_score": 90.0,
            "identified_gaps": [],
            "submission_ready": True,
            "precedent_win_rate": 0.85,
            "merchant_ratio": 0.3,
            "expected_decision": "AUTO_SUBMIT",
            "min_score": 80.0,
            "max_score": 100.0,
        },
        {
            "id": 5,
            "name": "Digital Goods INR with failed download",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 79.00,
            "overall_strength_score": 62.0,
            "identified_gaps": ["Digital download telemetry indicates HTTP 500 error during buyer access"],
            "submission_ready": True,
            "precedent_win_rate": 0.65,
            "merchant_ratio": 0.7,
            "expected_decision": "DRAFT_PENDING_REVIEW",
            "min_score": 60.0,
            "max_score": 79.9,
        },
        {
            "id": 6,
            "name": "SNAD with catalog SKU match",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            "amount": 140.00,
            "overall_strength_score": 70.0,
            "identified_gaps": ["Buyer claims color mismatch despite product catalog SKU match"],
            "submission_ready": True,
            "precedent_win_rate": 0.75,
            "merchant_ratio": 0.5,
            "expected_decision": "DRAFT_PENDING_REVIEW",
            "min_score": 60.0,
            "max_score": 85.0,
        },
        {
            "id": 7,
            "name": "SNAD with warehouse packing error",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            "amount": 160.00,
            "overall_strength_score": 25.0,
            "identified_gaps": ["Warehouse barcode log indicates incorrect item variant was dispatched"],
            "submission_ready": False,
            "precedent_win_rate": 0.30,
            "merchant_ratio": 1.1,
            "expected_decision": "ESCALATE_TO_HUMAN",
            "min_score": 0.0,
            "max_score": 59.9,
        },
        {
            "id": 8,
            "name": "Unauthorized charge with verified address match",
            "reason": "UNAUTHORIZED",
            "amount": 110.00,
            "overall_strength_score": 92.0,
            "identified_gaps": [],
            "submission_ready": True,
            "precedent_win_rate": 0.88,
            "merchant_ratio": 0.4,
            "expected_decision": "AUTO_SUBMIT",
            "min_score": 80.0,
            "max_score": 100.0,
        },
        {
            "id": 9,
            "name": "Unauthorized charge with unauthorized freight reroute",
            "reason": "UNAUTHORIZED",
            "amount": 220.00,
            "overall_strength_score": 35.0,
            "identified_gaps": ["Carrier telemetry confirms shipment was rerouted to unconfirmed address"],
            "submission_ready": False,
            "precedent_win_rate": 0.35,
            "merchant_ratio": 1.6,
            "expected_decision": "ESCALATE_TO_HUMAN",
            "min_score": 0.0,
            "max_score": 59.9,
        },
        {
            "id": 10,
            "name": "High-Value claim ($850) missing signature receipt",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": 850.00,
            "overall_strength_score": 85.0,
            "identified_gaps": ["Missing carrier signature confirmation for transaction over $750 threshold"],
            "submission_ready": True,
            "precedent_win_rate": 0.80,
            "merchant_ratio": 0.5,
            "expected_decision": "DRAFT_PENDING_REVIEW",
            "min_score": 60.0,
            "max_score": 85.0,
        },
    ]


def test_scenario_matrix():
    print("=" * 75)
    print("  DISPUTESHIELD AI — 10-SCENARIO DECISION MATRIX HARNESS")
    print("=" * 75)

    scorer = ConfidenceScorer()
    scenarios = get_scenario_definitions()
    passed_count = 0

    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Idempotent cleanup of any prior test run records
        db.query(Dispute).filter(Dispute.paypal_dispute_id.like("PP-SCENARIO-%")).delete()
        db.commit()

        for sc in scenarios:
            strategy_report = EvidenceStrategyReport(
                dispute_id=f"PP-SCENARIO-{sc['id']:02d}",
                category=sc["reason"],
                overall_strength_score=sc["overall_strength_score"],
                items=[],
                identified_gaps=sc["identified_gaps"],
                recommended_action=(
                    "Execute autonomous counter-evidence submission directly to PayPal."
                    if sc["expected_decision"] == "AUTO_SUBMIT"
                    else "Queue compiled evidence draft in AG Grid dashboard for 1-click merchant review."
                    if sc["expected_decision"] == "DRAFT_PENDING_REVIEW"
                    else "Escalate dispute to merchant risk team."
                ),
                can_auto_submit=(sc["expected_decision"] == "AUTO_SUBMIT"),
            )

            compiled_payload = CompiledEvidencePayload(
                dispute_id=f"PP-SCENARIO-{sc['id']:02d}",
                evidence_type="PROOF_OF_FULFILLMENT",
                notes=f"Auto-compiled defense statement for {sc['name']}",
                tracking_info=[{"carrier": "UPS", "tracking_number": "1Z9999999999999999"}] if sc["submission_ready"] else None,
                documents=[],
                submission_ready=sc["submission_ready"],
            )

            decision_res: ConfidenceDecision = scorer.calculate_decision(
                strategy_report=strategy_report,
                compiled_payload=compiled_payload,
                dispute_data={"dispute_amount": sc["amount"]},
                merchant_data={"dispute_ratio": sc["merchant_ratio"]},
                precedent_win_rate=sc["precedent_win_rate"],
            )

            # Assert Decision
            assert decision_res.decision == sc["expected_decision"], (
                f"Scenario {sc['id']} ({sc['name']}) FAILED: Expected {sc['expected_decision']}, "
                f"got {decision_res.decision} (score={decision_res.confidence_score})"
            )

            # Assert Score Range
            assert sc["min_score"] <= decision_res.confidence_score <= sc["max_score"], (
                f"Scenario {sc['id']} score out of bounds: {decision_res.confidence_score} not in [{sc['min_score']}, {sc['max_score']}]"
            )

            # Verify Database Model mapping
            dispute_rec = Dispute(
                paypal_dispute_id=f"PP-SCENARIO-{sc['id']:02d}",
                reason=sc["reason"],
                dispute_amount=sc["amount"],
                dispute_currency="USD",
                status=DisputeStatus.UNDER_REVIEW.value if decision_res.decision == "AUTO_SUBMIT" else DisputeStatus.OPEN.value,
                agent_decision=(
                    AgentDecision.AUTO_SUBMITTED.value
                    if decision_res.decision == "AUTO_SUBMIT"
                    else AgentDecision.DRAFT_PENDING_REVIEW.value
                    if decision_res.decision == "DRAFT_PENDING_REVIEW"
                    else AgentDecision.ESCALATED.value
                ),
                confidence_score=decision_res.confidence_score / 100.0,
                agent_reasoning=decision_res.decision_rationale,
            )
            db.add(dispute_rec)
            db.flush()

            passed_count += 1
            print(
                f" [PASSED] Scenario {sc['id']:02d}: {sc['name']:<55} | "
                f"Decision: {decision_res.decision:<20} | Score: {decision_res.confidence_score:5.1f}%"
            )

        db.commit()
    finally:
        db.close()

    print("=" * 75)
    print(f" RESULT: {passed_count}/{len(scenarios)} SCENARIOS PASSED WITH ZERO FAILURES")
    print("=" * 75)


if __name__ == "__main__":
    test_scenario_matrix()
