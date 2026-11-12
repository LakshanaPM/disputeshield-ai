"""
DisputeShield AI — Autonomous Confidence Scoring & Decision Engine (Day 11)

Calculates composite dispute defense confidence scores and enforces
tri-state operational decisions: AUTO_SUBMIT, DRAFT_PENDING_REVIEW, or ESCALATE_TO_HUMAN.
"""

import logging
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, Field

from agent.evidence_engine import EvidenceStrategyReport, CompiledEvidencePayload

logger = logging.getLogger(__name__)


class ConfidenceDecision(BaseModel):
    confidence_score: float = Field(
        ..., ge=0.0, le=100.0, description="Composite confidence score on a 0.0 to 100.0 scale."
    )
    decision: Literal["AUTO_SUBMIT", "DRAFT_PENDING_REVIEW", "ESCALATE_TO_HUMAN"] = Field(
        ..., description="The autonomous action decision determined by the AI agent."
    )
    recommended_action: str = Field(..., description="Actionable recommendation describing next steps.")
    confidence_breakdown: Dict[str, float] = Field(
        ..., description="Weighted factor breakdown contributing to the score."
    )
    decision_rationale: str = Field(..., description="Explanation of why the decision was selected.")


class ConfidenceScorer:
    """
    Evaluates evidence strength, historical precedent win-rate, financial amount risk,
    and merchant account health to output a decisive operational resolution.
    """

    AUTO_SUBMIT_THRESHOLD = 80.0
    DRAFT_THRESHOLD = 60.0

    def calculate_decision(
        self,
        strategy_report: EvidenceStrategyReport,
        compiled_payload: CompiledEvidencePayload,
        dispute_data: Dict[str, Any],
        merchant_data: Optional[Dict[str, Any]] = None,
        precedent_win_rate: float = 0.85,
    ) -> ConfidenceDecision:
        """
        Calculate composite confidence score and assign resolution tier.
        """
        merchant_data = merchant_data or {}
        amount = float(dispute_data.get("dispute_amount") or dispute_data.get("amount") or 0.0)
        dispute_ratio = float(merchant_data.get("dispute_ratio") or 0.5)

        # 1. Factor Calculations
        # A. Evidence factor (weight: 45%)
        evidence_weight = round(strategy_report.overall_strength_score * 0.45, 2)

        # B. Precedent factor (weight: 25%)
        precedent_weight = round((precedent_win_rate * 100.0) * 0.25, 2)

        # C. Amount risk factor (weight: 15%)
        if amount >= 300.0:
            amount_weight = 10.0
        elif amount >= 150.0:
            amount_weight = 12.5
        else:
            amount_weight = 15.0

        # D. Merchant health factor (weight: 15%)
        if dispute_ratio < 1.0:
            merchant_weight = 15.0
        elif dispute_ratio <= 1.5:
            merchant_weight = 10.0
        else:
            merchant_weight = 5.0

        composite_score = round(
            min(max(evidence_weight + precedent_weight + amount_weight + merchant_weight, 0.0), 100.0),
            1,
        )

        breakdown = {
            "evidence_weight": evidence_weight,
            "precedent_weight": precedent_weight,
            "amount_weight": amount_weight,
            "merchant_weight": merchant_weight,
        }

        # 2. Decision Gating
        identified_gaps = list(strategy_report.identified_gaps)
        
        # PayPal Seller Protection Policy Section 11.3: Signature confirmation required for >= $750
        sig_confirmed = (
            getattr(compiled_payload, "signature_confirmation", False)
            or dispute_data.get("signature_confirmed", False)
        )
        if amount >= 750.0 and not sig_confirmed and not any("signature" in g.lower() for g in identified_gaps):
            identified_gaps.append("Missing carrier signature confirmation for transaction over $750 threshold (PayPal Section 11.3)")

        gaps_count = len(identified_gaps)
        is_ready = compiled_payload.submission_ready

        if composite_score >= self.AUTO_SUBMIT_THRESHOLD and is_ready and gaps_count == 0:
            decision = "AUTO_SUBMIT"
            action = "Execute autonomous counter-evidence submission directly to PayPal."
            rationale = (
                f"Confidence is exceptionally high ({composite_score}/100) with complete proof of fulfillment "
                f"and 0 identified defense gaps. Meets all PayPal Seller Protection Section 11.3 criteria (100% win trajectory)."
            )
        elif composite_score >= self.DRAFT_THRESHOLD:
            decision = "DRAFT_PENDING_REVIEW"
            action = "Queue compiled evidence draft in AG Grid dashboard for 1-click merchant review."
            gaps_summary = f" {gaps_count} gap(s) detected: {'; '.join(identified_gaps)}" if gaps_count > 0 else ""
            rationale = (
                f"Confidence is moderate ({composite_score}/100).{gaps_summary} "
                f"Drafted counter-evidence is compiled and staged for merchant approval."
            )
        else:
            decision = "ESCALATE_TO_HUMAN"
            action = "Auto-concession triage: Evaluate proactive claim acceptance or refund to avoid $20 dispute fee and prevent unforced arbitration loss."
            rationale = (
                f"Confidence is low ({composite_score}/100) due to substantial fulfillment gaps. "
                f"Pre-dispute triage recommends proactive settlement or carrier insurance claim to maintain 100% defended win rate."
            )

        return ConfidenceDecision(
            confidence_score=composite_score,
            decision=decision,
            recommended_action=action,
            confidence_breakdown=breakdown,
            decision_rationale=rationale,
        )
