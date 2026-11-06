"""
DisputeShield AI — Evidence Strategy Engine Tests (Day 9)

Validates:
1. Complete INR with DELIVERED status and postal match -> Score >= 85, can_auto_submit == True, no gaps.
2. Incomplete INR with IN_TRANSIT status -> Score < 60, gap mentions DELIVERED status, can_auto_submit == False.
3. SNAD with catalog specs but missing inspection logs -> Correct gap flagged, balanced score.
4. Unauthorized transaction with verified shipping address match -> High strength score (>= 85), can_auto_submit == True.
"""

import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_evidence_engine.db"
sys.path.insert(0, "backend")

from agent.dispute_agent import TriageResult
from agent.evidence_engine import (
    EvidenceStrategyEngine,
    EvidenceStrategyReport,
    CompiledEvidencePayload,
    EvidenceItem,
)



def test_complete_inr_delivered():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="INR",
        severity_score=65.0,
        urgency_level="MEDIUM",
        recommended_strategy="Submit Proof of Delivery",
        required_evidence_types=["PROOF_OF_DELIVERY", "CARRIER_CONFIRMATION"],
        reasoning_summary="Carrier tracking shows delivered.",
    )
    evidence_chain = {
        "shipping": {
            "carrier": "UPS",
            "tracking_number": "1Z9999999999999999",
            "delivery_status": "DELIVERED",
            "delivered_at": "2026-10-18T14:30:00Z",
            "proof_of_delivery_available": True,
            "proof_of_delivery": {
                "postal_code_match": True,
                "signed_by": "J. Buyer",
            },
        }
    }
    dispute_data = {"dispute_id": "PP-D-INR-100", "buyer_email": "buyer@example.com"}

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    assert isinstance(report, EvidenceStrategyReport)
    assert report.category == "INR"
    assert report.overall_strength_score >= 85.0
    assert report.can_auto_submit is True
    assert len(report.identified_gaps) == 0
    print("[TEST 1 PASSED: Complete INR with DELIVERED status scored >= 85 and flagged can_auto_submit=True]")


def test_incomplete_inr_in_transit():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="INR",
        severity_score=75.0,
        urgency_level="HIGH",
        recommended_strategy="Hold for delivery",
        required_evidence_types=["PROOF_OF_DELIVERY"],
        reasoning_summary="In transit.",
    )
    evidence_chain = {
        "shipping": {
            "carrier": "FEDEX",
            "tracking_number": "794644790132",
            "delivery_status": "IN_TRANSIT",
            "proof_of_delivery_available": False,
        }
    }
    dispute_data = {"dispute_id": "PP-D-INR-101"}

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    assert isinstance(report, EvidenceStrategyReport)
    assert report.category == "INR"
    assert report.overall_strength_score < 60.0
    assert report.can_auto_submit is False
    assert any("DELIVERED status" in gap for gap in report.identified_gaps)
    print("[TEST 2 PASSED: Incomplete INR with IN_TRANSIT correctly flagged DELIVERED gap with can_auto_submit=False]")


def test_snad_missing_inspection_photos():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="SNAD",
        severity_score=60.0,
        urgency_level="MEDIUM",
        recommended_strategy="Submit catalog specifications",
        required_evidence_types=["PRODUCT_CATALOG", "INVOICE"],
        reasoning_summary="Item description match.",
    )
    evidence_chain = {
        "order": {
            "items": [
                {
                    "name": "Wireless Noise-Canceling Headphones",
                    "sku": "HEADPHONE-NC-01",
                    "description": "Black over-ear Bluetooth 5.3 headphones with ANC.",
                }
            ]
        },
        "invoice": {"items": [{"name": "Wireless Noise-Canceling Headphones"}]},
        # Note: missing pre-shipment inspection photos
    }
    dispute_data = {"dispute_id": "PP-D-SNAD-102"}

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    assert isinstance(report, EvidenceStrategyReport)
    assert report.category == "SNAD"
    assert any("inspection" in gap.lower() for gap in report.identified_gaps)
    # Score should reflect catalog presence (35% + 25% + 12% ~ 72%)
    assert 60.0 <= report.overall_strength_score <= 80.0
    print("[TEST 3 PASSED: SNAD with catalog specs but missing inspection logs correctly flagged gap]")


def test_unauthorized_with_verified_address():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="UNAUTHORIZED",
        severity_score=70.0,
        urgency_level="MEDIUM",
        recommended_strategy="Submit verified shipping address match",
        required_evidence_types=["BILLING_ADDRESS_MATCH", "ORDER_CONFIRMATION"],
        reasoning_summary="Verified address match.",
    )
    evidence_chain = {
        "order": {
            "shipping": {
                "address": {
                    "address_line_1": "123 Main St",
                    "city": "San Jose",
                    "state": "CA",
                    "postal_code": "95131",
                }
            }
        },
        "authentication_logs": {
            "ip": "192.168.1.1",
            "2fa_verified": True,
        },
    }
    dispute_data = {
        "dispute_id": "PP-D-UNAUTH-103",
        "buyer_email": "jane@example.com",
        "shipping_address_verified": True,
        "authentication_logs": True,
    }

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    assert isinstance(report, EvidenceStrategyReport)
    assert report.category == "UNAUTHORIZED"
    assert report.overall_strength_score >= 85.0
    assert report.can_auto_submit is True
    assert len(report.identified_gaps) == 0
    print("[TEST 4 PASSED: Unauthorized transaction with verified address scored >= 85 with can_auto_submit=True]")


async def test_compile_evidence_inr():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="INR",
        severity_score=65.0,
        urgency_level="MEDIUM",
        recommended_strategy="Submit Proof of Delivery",
        required_evidence_types=["PROOF_OF_DELIVERY"],
        reasoning_summary="Delivered.",
    )
    evidence_chain = {
        "order": {"order_id": "ORD-8822", "items": [{"name": "Wireless Headphones", "sku": "HP-01"}]},
        "shipping": {
            "carrier": "UPS",
            "tracking_number": "1Z9999999999999999",
            "delivery_status": "DELIVERED",
            "delivered_at": "2026-10-18T14:30:00Z",
            "proof_of_delivery_available": True,
            "proof_of_delivery": {"postal_code_match": True, "signed_by": "J. Buyer"},
        },
    }
    dispute_data = {"dispute_id": "PP-D-INR-201", "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED"}

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    payload = await engine.compile_evidence(report, evidence_chain, dispute_data)

    assert isinstance(payload, CompiledEvidencePayload)
    assert payload.evidence_type == "PROOF_OF_FULFILLMENT"
    assert payload.tracking_info is not None
    assert payload.tracking_info[0]["tracking_number"] == "1Z9999999999999999"
    assert payload.tracking_info[0]["carrier_name"] == "UPS"
    assert "1Z9999999999999999" in payload.notes
    assert "ORD-8822" in payload.notes
    assert payload.submission_ready is True
    print("[TEST 5 PASSED: Compiled INR evidence produces valid tracking info, notes, and submission_ready=True]")


async def test_compile_evidence_snad():
    engine = EvidenceStrategyEngine()
    triage = TriageResult(
        dispute_category="SNAD",
        severity_score=60.0,
        urgency_level="MEDIUM",
        recommended_strategy="Submit catalog specifications",
        required_evidence_types=["PRODUCT_CATALOG", "INVOICE"],
        reasoning_summary="Catalog match.",
    )
    evidence_chain = {
        "order": {"order_id": "ORD-5544", "items": [{"name": "Mechanical Keyboard", "sku": "KB-RGB-01"}]},
        "invoice": {"items": [{"name": "Mechanical Keyboard"}]},
    }
    dispute_data = {"dispute_id": "PP-D-SNAD-202", "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED"}

    report = engine.evaluate_strategy(triage, evidence_chain, dispute_data)
    payload = await engine.compile_evidence(report, evidence_chain, dispute_data)

    assert isinstance(payload, CompiledEvidencePayload)
    assert payload.evidence_type == "PROOF_OF_SIGNIFICANT_NOT_AS_DESCRIBED"
    assert "KB-RGB-01" in payload.notes or "Mechanical Keyboard" in payload.notes
    assert "policy" in payload.notes.lower()
    assert "ORD-5544" in payload.notes
    print("[TEST 6 PASSED: Compiled SNAD evidence references SKU, catalog, and return policy]")


def run_all_tests():
    print("=" * 60)
    print("DisputeShield AI — Running Day 9 & 10 Evidence Engine Tests")
    print("=" * 60)

    test_complete_inr_delivered()
    test_incomplete_inr_in_transit()
    test_snad_missing_inspection_photos()
    test_unauthorized_with_verified_address()

    import asyncio
    asyncio.run(test_compile_evidence_inr())
    asyncio.run(test_compile_evidence_snad())

    print("=" * 60)
    print("ALL DAY 9 & 10 EVIDENCE ENGINE TESTS PASSED SUCCESSFULLY (6/6)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()

