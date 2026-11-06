"""
DisputeShield AI — Agent Triage Logic (Day 8)

Analyzes disputes, calculates severity and urgency based on response deadlines,
claim amounts, and merchant health, and outputs structured triage decisions.
Supports Gemini 2.0 Flash, OpenAI GPT-4o, and heuristic fallback engine.
"""

from datetime import datetime, timezone
import json
import logging
import os
import re
from typing import Any, Dict, List, Literal, Optional, Tuple
from pydantic import BaseModel, Field

from config import settings
from agent.prompts import DISPUTE_AGENT_SYSTEM_PROMPT, TRIAGE_PROMPT_TEMPLATE
from agent.tools import get_agent_tools

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Structured Triage Output Schema
# ---------------------------------------------------------------------------

class TriageResult(BaseModel):
    dispute_category: Literal["INR", "SNAD", "UNAUTHORIZED", "CANCELLATION", "OTHER"] = Field(
        ...,
        description="Standard dispute category classification.",
    )
    severity_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Dispute severity score from 0.0 (negligible) to 100.0 (critical).",
    )
    urgency_level: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"] = Field(
        ...,
        description="Operational urgency level derived from deadline proximity.",
    )
    recommended_strategy: str = Field(
        ...,
        description="Recommended counter-evidence strategy or action.",
    )
    required_evidence_types: List[str] = Field(
        default_factory=list,
        description="List of specific evidence types needed to defend the dispute.",
    )
    reasoning_summary: str = Field(
        ...,
        description="Concise rationale explaining the triage classification and strategy.",
    )


# ---------------------------------------------------------------------------
# Dispute Triage Agent
# ---------------------------------------------------------------------------

class DisputeTriageAgent:
    """
    Triage Agent responsible for categorizing claims, assessing severity,
    and synthesizing optimal PayPal defense strategies.
    """

    def __init__(
        self,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        self.llm = None
        gemini_key = api_key or getattr(settings, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
        openai_key = api_key or getattr(settings, "openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")

        # 1. Primary Model: Gemini 2.0 Flash
        if gemini_key:
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                model = model_name or getattr(settings, "gemini_model", "gemini-2.0-flash")
                self.llm = ChatGoogleGenerativeAI(
                    model=model,
                    google_api_key=gemini_key,
                    temperature=0.1,
                )
                logger.info(f"Initialized DisputeTriageAgent with Gemini model: {model}")
            except Exception as exc:
                logger.warning(f"Failed to initialize Gemini LLM: {exc}")

        # 2. Secondary Model: OpenAI GPT-4o
        if not self.llm and openai_key:
            try:
                from langchain_openai import ChatOpenAI
                model = model_name or getattr(settings, "openai_model", "gpt-4o")
                self.llm = ChatOpenAI(
                    model=model,
                    api_key=openai_key,
                    temperature=0.1,
                )
                logger.info(f"Initialized DisputeTriageAgent with OpenAI model: {model}")
            except Exception as exc:
                logger.warning(f"Failed to initialize OpenAI LLM: {exc}")

        if not self.llm:
            logger.info("DisputeTriageAgent initialized in deterministic heuristic mode (no LLM keys configured).")

        # Bind agent tools directly so tools are integrated in agent capabilities
        self.tools = get_agent_tools()
        self.tools_by_name = {tool.name: tool for tool in self.tools}

    async def inspect_dispute_context_via_tools(
        self,
        dispute_id: str,
        order_id: Optional[str] = None,
        tracking_number: Optional[str] = None,
        invoice_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Dynamically query external context, orders, and tracking records via registered tools
        prior to final evidence synthesis.
        """
        inspected = {}
        if dispute_id and "paypal_get_dispute" in self.tools_by_name:
            try:
                tool = self.tools_by_name["paypal_get_dispute"]
                inspected["dispute"] = await tool.ainvoke({"dispute_id": dispute_id})
            except Exception as exc:
                logger.warning(f"Tool paypal_get_dispute failed for {dispute_id}: {exc}")

        if order_id and "paypal_lookup_order" in self.tools_by_name:
            try:
                tool = self.tools_by_name["paypal_lookup_order"]
                inspected["order"] = await tool.ainvoke({"order_id": order_id})
            except Exception as exc:
                logger.warning(f"Tool paypal_lookup_order failed for {order_id}: {exc}")

        if tracking_number and "paypal_get_tracking" in self.tools_by_name:
            try:
                tool = self.tools_by_name["paypal_get_tracking"]
                inspected["tracking"] = await tool.ainvoke({"tracking_number": tracking_number})
            except Exception as exc:
                logger.warning(f"Tool paypal_get_tracking failed for {tracking_number}: {exc}")

        if invoice_id and "paypal_get_invoice" in self.tools_by_name:
            try:
                tool = self.tools_by_name["paypal_get_invoice"]
                inspected["invoice"] = await tool.ainvoke({"invoice_id": invoice_id})
            except Exception as exc:
                logger.warning(f"Tool paypal_get_invoice failed for {invoice_id}: {exc}")

        return inspected

    def calculate_severity_and_urgency(
        self,
        amount: float,
        response_deadline: Optional[Any] = None,
        merchant_dispute_ratio: float = 0.0,
    ) -> Tuple[float, str, float]:
        """
        Calculate severity score and urgency level based on claim amount,
        hours remaining until response deadline, and merchant account risk.
        Returns: (severity_score, urgency_level, hours_remaining)
        """
        # 1. Hours remaining calculation
        hours_remaining = 72.0  # default assumption if missing
        if response_deadline:
            if isinstance(response_deadline, str):
                try:
                    cleaned_date = response_deadline.replace("Z", "+00:00")
                    dt = datetime.fromisoformat(cleaned_date)
                    now = datetime.now(timezone.utc)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    delta = dt - now
                    hours_remaining = max(delta.total_seconds() / 3600.0, 0.0)
                except Exception:
                    hours_remaining = 72.0
            elif isinstance(response_deadline, datetime):
                now = datetime.now(timezone.utc)
                dt = response_deadline if response_deadline.tzinfo else response_deadline.replace(tzinfo=timezone.utc)
                hours_remaining = max((dt - now).total_seconds() / 3600.0, 0.0)

        # 2. Urgency classification
        if hours_remaining <= 12.0:
            urgency = "CRITICAL"
            urgency_score = 40.0
        elif hours_remaining <= 24.0:
            urgency = "HIGH"
            urgency_score = 25.0
        elif hours_remaining <= 72.0:
            urgency = "MEDIUM"
            urgency_score = 15.0
        else:
            urgency = "LOW"
            urgency_score = 5.0

        # 3. Amount impact
        if amount >= 300.0:
            amount_score = 35.0
        elif amount >= 150.0:
            amount_score = 25.0
        elif amount >= 75.0:
            amount_score = 15.0
        else:
            amount_score = 10.0

        # 4. Merchant risk ratio impact (PayPal thresholds: 1.0% is standard; 1.5% is high risk)
        if merchant_dispute_ratio >= 1.5:
            ratio_score = 25.0
        elif merchant_dispute_ratio >= 1.0:
            ratio_score = 15.0
        else:
            ratio_score = 5.0

        total_severity = min(max(amount_score + urgency_score + ratio_score, 10.0), 100.0)
        return round(total_severity, 1), urgency, round(hours_remaining, 1)

    def _heuristic_triage(
        self,
        dispute_data: Dict[str, Any],
        evidence_chain: Optional[Dict[str, Any]],
        severity_score: float,
        urgency_level: str,
    ) -> TriageResult:
        """Deterministic heuristic fallback evaluating dispute categorization and defense strategy."""
        reason = str(dispute_data.get("reason", "")).upper()
        buyer_message = str(dispute_data.get("buyer_message", "")).lower()

        # Check evidence chain attributes
        is_digital = False
        delivery_status = "NOT_FOUND"
        if evidence_chain:
            shipping = evidence_chain.get("shipping", {})
            delivery_status = shipping.get("delivery_status", "NOT_FOUND")
            invoice = evidence_chain.get("invoice", {})
            if invoice and (invoice.get("digital_delivery_confirmed") or "license" in str(evidence_chain).lower()):
                is_digital = True

        # Category mapping
        if "NOT_RECEIVED" in reason or any(kw in buyer_message for kw in ["not received", "didn't receive", "missing package", "never arrived", "no delivery"]):
            category = "INR"
        elif "NOT_AS_DESCRIBED" in reason or any(kw in buyer_message for kw in ["color", "defective", "damaged", "scratched", "broken", "fake", "counterfeit", "different"]):
            category = "SNAD"
        elif "UNAUTHORISED" in reason or "UNAUTHORIZED" in reason or any(kw in buyer_message for kw in ["unauthorized", "didn't make this purchase", "compromised", "fraud"]):
            category = "UNAUTHORIZED"
        elif "CANCEL" in reason or "RETURN" in reason:
            category = "CANCELLATION"
        else:
            category = "OTHER"

        # Strategy and required evidence formulation
        if category == "INR":
            if is_digital:
                strategy = "Submit Proof of Digital Delivery including paid invoice recipient verification, access logs, and license key activation confirmation."
                evidence_types = ["DIGITAL_INVOICE", "LICENSE_ACTIVATION_LOG", "BILLING_RECIPIENT_MATCH"]
                reasoning = "Dispute involves digital merchandise/services. Defense relies on electronic access confirmation and payment receipt."
            elif delivery_status == "DELIVERED":
                strategy = "Submit carrier Proof of Delivery showing DELIVERED status with recipient postal code match to invoke PayPal Seller Protection."
                evidence_types = ["PROOF_OF_DELIVERY", "CARRIER_CONFIRMATION", "TRACKING_NUMBER"]
                reasoning = "Carrier tracking confirms successful delivery to the buyer's destination. Merchant is covered under PayPal Seller Protection."
            else:
                strategy = "Provide active shipment tracker and carrier transit updates; monitor for delivery confirmation before deadline."
                evidence_types = ["TRACKING_NUMBER", "CARRIER_IN_TRANSIT_RECEIPT"]
                reasoning = "Item appears in transit or unconfirmed. Provide tracking details and check for carrier delivery scan."

        elif category == "SNAD":
            strategy = "Submit original product catalog specification, clear invoice line-item match, and return policy terms demonstrating item delivered matches description."
            evidence_types = ["ITEM_SPECIFICATION", "PRODUCT_CATALOG", "INVOICE", "RETURN_POLICY"]
            reasoning = "Buyer alleges item differs from description. Merchant catalog specs and itemized order data substantiate fulfillment accuracy."

        elif category == "UNAUTHORIZED":
            strategy = "Submit proof of authorized access including cardholder billing address verification match, order confirmation sent to verified email, and 2FA/IP logs."
            evidence_types = ["BILLING_ADDRESS_MATCH", "ORDER_CONFIRMATION", "AUTHENTICATION_LOGS"]
            reasoning = "Claim of unauthorized charge. Seller Protection applies when fulfilled to the verified PayPal shipping address."

        elif category == "CANCELLATION":
            strategy = "Provide timestamped proof of shipment prior to cancellation notice, or terms of sale agreement."
            evidence_types = ["FULFILLMENT_TIMESTAMP", "TERMS_OF_SERVICE"]
            reasoning = "Cancellation dispute requires proof order was already fulfilled or dispatched before cancellation request was submitted."

        else:
            strategy = "Gather transaction logs, buyer communications, and proof of fulfillment."
            evidence_types = ["TRANSACTION_LOG", "BUYER_COMMUNICATIONS"]
            reasoning = "General dispute claim. Provide complete transaction timeline."

        return TriageResult(
            dispute_category=category,
            severity_score=severity_score,
            urgency_level=urgency_level,
            recommended_strategy=strategy,
            required_evidence_types=evidence_types,
            reasoning_summary=reasoning,
        )

    async def triage_dispute(
        self,
        dispute_data: Dict[str, Any],
        evidence_chain: Optional[Dict[str, Any]] = None,
        historical_precedents: Optional[str] = None,
    ) -> TriageResult:
        """
        Execute full dispute triage.
        Uses structured LLM output if available, otherwise executes deterministic heuristic triage.
        """
        amount = float(dispute_data.get("dispute_amount") or dispute_data.get("amount") or 0.0)
        deadline = dispute_data.get("response_deadline") or dispute_data.get("buyer_response_due_date")
        ratio = float(dispute_data.get("merchant_dispute_ratio") or 0.0)

        severity_score, urgency_level, hours_remaining = self.calculate_severity_and_urgency(
            amount=amount,
            response_deadline=deadline,
            merchant_dispute_ratio=ratio,
        )

        # Attempt structured LLM triage if configured
        if self.llm:
            try:
                order_info = (evidence_chain or {}).get("order", {})
                shipping_info = (evidence_chain or {}).get("shipping", {})
                invoice_info = (evidence_chain or {}).get("invoice", {})

                prompt = TRIAGE_PROMPT_TEMPLATE.format(
                    dispute_id=dispute_data.get("dispute_id") or dispute_data.get("paypal_dispute_id", "UNKNOWN"),
                    reason=dispute_data.get("reason", "OTHER"),
                    amount=amount,
                    currency=dispute_data.get("dispute_currency", "USD"),
                    buyer_message=dispute_data.get("buyer_message", "No message provided."),
                    response_deadline=deadline or "Not specified",
                    hours_remaining=hours_remaining,
                    order_id=order_info.get("order_id") or order_info.get("id", "N/A"),
                    items_summary=json.dumps(order_info.get("items", [])),
                    carrier=shipping_info.get("carrier", "N/A"),
                    tracking_number=shipping_info.get("tracking_number", "N/A"),
                    delivery_status=shipping_info.get("delivery_status", "UNKNOWN"),
                    digital_delivery_confirmed=bool(invoice_info.get("digital_delivery_confirmed")),
                    historical_precedents=historical_precedents or "[]",
                )

                structured_llm = self.llm.with_structured_output(TriageResult)
                res = await structured_llm.ainvoke([
                    {"role": "system", "content": DISPUTE_AGENT_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ])
                if isinstance(res, TriageResult):
                    # Harmonize calculated severity and urgency
                    res.severity_score = max(res.severity_score, severity_score)
                    if urgency_level == "CRITICAL":
                        res.urgency_level = "CRITICAL"
                    return res
            except Exception as exc:
                logger.warning(f"LLM triage call failed: {exc}; utilizing heuristic triage engine.")

        # Deterministic fallback
        return self._heuristic_triage(
            dispute_data=dispute_data,
            evidence_chain=evidence_chain,
            severity_score=severity_score,
            urgency_level=urgency_level,
        )
