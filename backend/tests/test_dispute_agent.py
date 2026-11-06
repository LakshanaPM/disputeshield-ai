"""
DisputeShield AI — Agent Triage Logic Tests (Day 8)

Validates 5 distinct dispute triage scenarios:
1. High-value INR ($350) with confirmed tracking delivered -> INR, High severity, tracking proof strategy.
2. SNAD ("Wrong item color") -> SNAD, Medium severity, catalog/invoice match strategy.
3. Unauthorized dispute -> UNAUTHORIZED, authentication/login records strategy.
4. Critical urgency dispute (< 12 hours remaining) -> urgency_level == "CRITICAL".
5. Digital goods INR -> Digital delivery invoice / license key access log recommendation.
"""

import asyncio
from datetime import datetime, timedelta, timezone
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_agent.db"
sys.path.insert(0, "backend")

from agent.dispute_agent import DisputeTriageAgent, TriageResult
from agent.tools import get_agent_tools


async def test_high_value_inr_delivered():
    agent = DisputeTriageAgent()
    dispute_data = {
        "dispute_id": "PP-D-INR-001",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 350.0,
        "dispute_currency": "USD",
        "buyer_message": "Package was never delivered to my address.",
    }
    evidence_chain = {
        "shipping": {
            "carrier": "UPS",
            "tracking_number": "1Z9999999999999999",
            "delivery_status": "DELIVERED",
        }
    }

    result = await agent.triage_dispute(dispute_data, evidence_chain)
    assert isinstance(result, TriageResult)
    assert result.dispute_category == "INR"
    assert result.severity_score >= 50.0  # High severity due to >$300 amount
    assert "Proof of Delivery" in result.recommended_strategy or "DELIVERED" in result.recommended_strategy
    assert "PROOF_OF_DELIVERY" in result.required_evidence_types
    print("[TEST 1 PASSED: High-value INR correctly categorized with Proof of Delivery strategy]")


async def test_snad_wrong_color():
    agent = DisputeTriageAgent()
    dispute_data = {
        "dispute_id": "PP-D-SNAD-002",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 120.0,
        "buyer_message": "The headphones received were blue instead of the black model I ordered.",
    }

    result = await agent.triage_dispute(dispute_data)
    assert isinstance(result, TriageResult)
    assert result.dispute_category == "SNAD"
    assert "catalog" in result.recommended_strategy.lower() or "specification" in result.recommended_strategy.lower()
    assert any("SPECIFICATION" in et or "CATALOG" in et or "INVOICE" in et for et in result.required_evidence_types)
    print("[TEST 2 PASSED: SNAD dispute correctly categorized with catalog/invoice match strategy]")


async def test_unauthorized_transaction():
    agent = DisputeTriageAgent()
    dispute_data = {
        "dispute_id": "PP-D-UNAUTH-003",
        "reason": "UNAUTHORISED",
        "dispute_amount": 89.0,
        "buyer_message": "Unfamiliar charge on my statement. I did not authorize this purchase.",
    }

    result = await agent.triage_dispute(dispute_data)
    assert isinstance(result, TriageResult)
    assert result.dispute_category == "UNAUTHORIZED"
    assert any(term in result.recommended_strategy.lower() for term in ["billing address", "authorized", "confirmation", "ip"])
    assert any("BILLING" in et or "ORDER" in et or "AUTHENTICATION" in et for et in result.required_evidence_types)
    print("[TEST 3 PASSED: Unauthorized transaction correctly categorized with authorization proof strategy]")


async def test_critical_urgency_deadline():
    agent = DisputeTriageAgent()
    deadline = (datetime.now(timezone.utc) + timedelta(hours=6)).isoformat()
    dispute_data = {
        "dispute_id": "PP-D-URGENT-004",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 180.0,
        "response_deadline": deadline,
        "buyer_message": "Item missing.",
    }

    result = await agent.triage_dispute(dispute_data)
    assert isinstance(result, TriageResult)
    assert result.urgency_level == "CRITICAL"
    assert result.severity_score >= 60.0  # Boosted by critical deadline proximity
    print("[TEST 4 PASSED: Critical deadline (<12h) correctly elevated urgency_level to CRITICAL]")


async def test_digital_goods_inr():
    agent = DisputeTriageAgent()
    dispute_data = {
        "dispute_id": "PP-D-DIGITAL-005",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 49.0,
        "buyer_message": "I never received the software activation code.",
    }
    evidence_chain = {
        "invoice": {
            "digital_delivery_confirmed": True,
            "items": [{"name": "Developer License Key"}],
        }
    }

    result = await agent.triage_dispute(dispute_data, evidence_chain)
    assert isinstance(result, TriageResult)
    assert result.dispute_category == "INR"
    assert "digital" in result.recommended_strategy.lower() or "license" in result.recommended_strategy.lower() or "access" in result.recommended_strategy.lower()
    assert any("DIGITAL" in et or "LICENSE" in et or "INVOICE" in et for et in result.required_evidence_types)
    print("[TEST 5 PASSED: Digital goods INR correctly recommends digital delivery and activation proof]")


def run_all_tests():
    print("=" * 60)
    print("DisputeShield AI — Running Day 8 Dispute Agent Triage Tests")
    print("=" * 60)

    # Verify agent tools registry
    tools = get_agent_tools()
    assert len(tools) == 6
    print("[REGISTRY CHECK PASSED: 6 agent tools loaded from MCP bridge]")

    # Run async triage scenario tests
    async def _run_suite():
        await test_high_value_inr_delivered()
        await test_snad_wrong_color()
        await test_unauthorized_transaction()
        await test_critical_urgency_deadline()
        await test_digital_goods_inr()

    asyncio.run(_run_suite())

    print("=" * 60)
    print("ALL DAY 8 DISPUTE AGENT TRIAGE TESTS PASSED SUCCESSFULLY (5/5)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
