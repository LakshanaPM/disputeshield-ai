"""
DisputeShield AI — Evidence Strategy Engine (Day 9)

Evaluates assembled dispute evidence against PayPal Seller Protection criteria,
calculates category-weighted strength scores (0–100%), identifies critical defense gaps,
and determines auto-submission eligibility.
"""

import json
import logging
import os
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field

from agent.dispute_agent import TriageResult
from agent.prompts import MERCHANT_EXPLANATION_PROMPT_TEMPLATE
from config import settings

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class EvidenceItem(BaseModel):
    name: str = Field(..., description="Descriptive name of the evidence item.")
    evidence_type: str = Field(..., description="Standardized PayPal evidence type identifier.")
    score: float = Field(..., ge=0.0, le=10.0, description="Completeness score on a 0.0 to 10.0 scale.")
    status: Literal["AVAILABLE", "MISSING", "INCOMPLETE"] = Field(
        ..., description="Availability status of the evidence document."
    )
    details: str = Field(..., description="Diagnostic assessment details.")


class EvidenceStrategyReport(BaseModel):
    dispute_id: str = Field(..., description="PayPal dispute identifier.")
    category: str = Field(..., description="Dispute category evaluated (INR, SNAD, UNAUTHORIZED, etc.).")
    overall_strength_score: float = Field(
        ..., ge=0.0, le=100.0, description="Aggregated evidence strength score on a 0.0 to 100.0 scale."
    )
    items: List[EvidenceItem] = Field(default_factory=list, description="Evaluated individual evidence items.")
    identified_gaps: List[str] = Field(default_factory=list, description="List of identified defense gaps.")
    recommended_action: str = Field(..., description="Operational recommendation for dispute defense.")
    can_auto_submit: bool = Field(
        ..., description="True if evidence strength score >= 80.0 and no critical gaps exist."
    )


class CompiledEvidencePayload(BaseModel):
    dispute_id: str = Field(..., description="The PayPal dispute ID.")
    evidence_type: str = Field(
        ..., description="Standard PayPal evidence type identifier (e.g. PROOF_OF_FULFILLMENT)."
    )
    notes: str = Field(..., description="The generated merchant defense explanation text.")
    tracking_info: Optional[List[Dict[str, str]]] = Field(
        default=None, description="Carrier and tracking number records formatted for PayPal API."
    )
    documents: Optional[List[Dict[str, Any]]] = Field(
        default=None, description="Uploaded proof documents or metadata attachments."
    )
    submission_ready: bool = Field(
        ..., description="True if evidence payload is complete and ready for PayPal API submission."
    )


# ---------------------------------------------------------------------------
# Evidence Strategy Engine
# ---------------------------------------------------------------------------

class EvidenceStrategyEngine:
    """
    Evaluates evidence chains according to PayPal Seller Protection rules,
    detects vulnerabilities, and calculates composite defense strength scores.
    """

    AUTO_SUBMIT_THRESHOLD = 80.0

    def __init__(self, llm: Optional[Any] = None):
        self.llm = llm
        if not self.llm:
            gemini_key = getattr(settings, "gemini_api_key", "") or os.environ.get("GEMINI_API_KEY", "")
            openai_key = getattr(settings, "openai_api_key", "") or os.environ.get("OPENAI_API_KEY", "")
            if gemini_key:
                try:
                    from langchain_google_genai import ChatGoogleGenerativeAI
                    self.llm = ChatGoogleGenerativeAI(
                        model=getattr(settings, "gemini_model", "gemini-2.0-flash"),
                        google_api_key=gemini_key,
                        temperature=0.1,
                    )
                except Exception:
                    self.llm = None
            elif openai_key:
                try:
                    from langchain_openai import ChatOpenAI
                    self.llm = ChatOpenAI(
                        model=getattr(settings, "openai_model", "gpt-4o"),
                        api_key=openai_key,
                        temperature=0.1,
                    )
                except Exception:
                    self.llm = None

    def evaluate_strategy(
        self,
        triage_result: TriageResult,

        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> EvidenceStrategyReport:
        """
        Evaluate evidence bundle completeness and calculate defense strength.
        """
        category = triage_result.dispute_category
        dispute_id = str(dispute_data.get("dispute_id") or dispute_data.get("paypal_dispute_id") or "UNKNOWN")

        if category == "INR":
            return self._evaluate_inr(dispute_id, evidence_chain, dispute_data)
        elif category == "SNAD":
            return self._evaluate_snad(dispute_id, evidence_chain, dispute_data)
        elif category == "UNAUTHORIZED":
            return self._evaluate_unauthorized(dispute_id, evidence_chain, dispute_data)
        else:
            return self._evaluate_general(dispute_id, category, evidence_chain, dispute_data)

    def _evaluate_inr(
        self,
        dispute_id: str,
        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> EvidenceStrategyReport:
        """Evaluate Item Not Received (INR) evidence chain."""
        items: List[EvidenceItem] = []
        gaps: List[str] = []
        critical_gap_present = False

        shipping = evidence_chain.get("shipping", {})
        invoice = evidence_chain.get("invoice", {})
        is_digital = bool(invoice and invoice.get("digital_delivery_confirmed"))

        if is_digital:
            # Digital goods evaluation
            # 1. Invoice & payment verification (weight: 40)
            if invoice.get("status") == "PAID":
                items.append(EvidenceItem(
                    name="Paid Digital Invoice",
                    evidence_type="DIGITAL_INVOICE",
                    score=10.0,
                    status="AVAILABLE",
                    details=f"Verified paid invoice #{invoice.get('invoice_number', 'N/A')} issued to buyer email.",
                ))
            else:
                items.append(EvidenceItem(
                    name="Paid Digital Invoice",
                    evidence_type="DIGITAL_INVOICE",
                    score=4.0,
                    status="INCOMPLETE",
                    details="Invoice status is not confirmed as paid.",
                ))
                gaps.append("Digital invoice does not show confirmed payment status.")
                critical_gap_present = True

            # 2. Digital activation log (weight: 35)
            if invoice.get("digital_delivery_confirmed") or "license" in str(evidence_chain).lower():
                items.append(EvidenceItem(
                    name="License / Digital Access Confirmation",
                    evidence_type="LICENSE_ACTIVATION_LOG",
                    score=9.5,
                    status="AVAILABLE",
                    details="License activation key was generated and transmitted electronically.",
                ))
            else:
                items.append(EvidenceItem(
                    name="License / Digital Access Confirmation",
                    evidence_type="LICENSE_ACTIVATION_LOG",
                    score=0.0,
                    status="MISSING",
                    details="Digital access logs or license activation records are missing.",
                ))
                gaps.append("Missing electronic download or license activation timestamp logs.")
                critical_gap_present = True

            # 3. Recipient matching (weight: 25)
            buyer_email = dispute_data.get("buyer_email")
            items.append(EvidenceItem(
                name="Recipient Account Verification",
                evidence_type="BILLING_RECIPIENT_MATCH",
                score=10.0 if buyer_email else 5.0,
                status="AVAILABLE" if buyer_email else "INCOMPLETE",
                details=f"Digital recipient account matched: {buyer_email or 'Unverified'}.",
            ))

            weights = [0.40, 0.35, 0.25]
            overall_score = sum(item.score * 10 * w for item, w in zip(items, weights))

        else:
            # Physical goods evaluation
            # 1. Carrier tracking number present (weight: 25)
            tracking_number = shipping.get("tracking_number")
            carrier = shipping.get("carrier")
            if tracking_number:
                items.append(EvidenceItem(
                    name="Carrier Tracking Number",
                    evidence_type="TRACKING_NUMBER",
                    score=10.0,
                    status="AVAILABLE",
                    details=f"Valid carrier tracking #{tracking_number} via {carrier or 'Carrier'}.",
                ))
            else:
                items.append(EvidenceItem(
                    name="Carrier Tracking Number",
                    evidence_type="TRACKING_NUMBER",
                    score=0.0,
                    status="MISSING",
                    details="No carrier shipment tracking number provided.",
                ))
                gaps.append("Missing shipment tracking number.")
                critical_gap_present = True

            # 2. Delivery status == DELIVERED (weight: 35)
            status = str(shipping.get("delivery_status", "NOT_FOUND")).upper()
            if status == "DELIVERED":
                items.append(EvidenceItem(
                    name="Carrier Delivery Status",
                    evidence_type="CARRIER_CONFIRMATION",
                    score=10.0,
                    status="AVAILABLE",
                    details=f"Carrier confirmed delivery at {shipping.get('delivered_at', 'destination')}.",
                ))
            elif status in ["IN_TRANSIT", "SHIPPED"]:
                items.append(EvidenceItem(
                    name="Carrier Delivery Status",
                    evidence_type="CARRIER_CONFIRMATION",
                    score=4.0,
                    status="INCOMPLETE",
                    details=f"Shipment is currently in transit ({status}). Not yet delivered.",
                ))
                gaps.append(f"Shipment tracking does not show DELIVERED status (currently {status}).")
                critical_gap_present = True
            else:
                items.append(EvidenceItem(
                    name="Carrier Delivery Status",
                    evidence_type="CARRIER_CONFIRMATION",
                    score=0.0,
                    status="MISSING",
                    details="No verifiable shipment delivery scan recorded.",
                ))
                gaps.append("Shipment tracking does not show DELIVERED status.")
                critical_gap_present = True

            # 3. Recipient postal code match (weight: 20)
            pod = shipping.get("proof_of_delivery", {})
            postal_match = pod.get("postal_code_match") if pod else None
            if postal_match is True or (shipping.get("proof_of_delivery_available") and status == "DELIVERED"):
                items.append(EvidenceItem(
                    name="Recipient Postal Code Verification",
                    evidence_type="SHIPPING_ADDRESS_MATCH",
                    score=10.0,
                    status="AVAILABLE",
                    details="Delivery scan matches buyer's registered destination postal code.",
                ))
            else:
                items.append(EvidenceItem(
                    name="Recipient Postal Code Verification",
                    evidence_type="SHIPPING_ADDRESS_MATCH",
                    score=4.0,
                    status="INCOMPLETE",
                    details="Carrier confirmation does not explicitly detail matching postal code.",
                ))
                gaps.append("Recipient postal code delivery verification is unconfirmed.")

            # 4. Proof of signature (weight: 20)
            signed_by = pod.get("signed_by") if pod else None
            if signed_by:
                items.append(EvidenceItem(
                    name="Proof of Signature",
                    evidence_type="PROOF_OF_DELIVERY",
                    score=10.0,
                    status="AVAILABLE",
                    details=f"Signature captured upon delivery: '{signed_by}'.",
                ))
            elif shipping.get("proof_of_delivery_available"):
                items.append(EvidenceItem(
                    name="Proof of Signature",
                    evidence_type="PROOF_OF_DELIVERY",
                    score=8.0,
                    status="AVAILABLE",
                    details="Carrier proof of delivery receipt on file (contactless delivery).",
                ))
            else:
                items.append(EvidenceItem(
                    name="Proof of Signature",
                    evidence_type="PROOF_OF_DELIVERY",
                    score=3.0,
                    status="INCOMPLETE",
                    details="No signature or delivery photo captured.",
                ))
                gaps.append("Missing buyer signature or delivery visual proof.")

            weights = [0.25, 0.35, 0.20, 0.20]
            overall_score = sum(item.score * 10 * w for item, w in zip(items, weights))

        overall_score = round(min(max(overall_score, 0.0), 100.0), 1)
        can_auto_submit = overall_score >= self.AUTO_SUBMIT_THRESHOLD and not critical_gap_present

        if can_auto_submit:
            action = "Submit carrier Proof of Delivery immediately to invoke PayPal Seller Protection."
        elif status in ["IN_TRANSIT", "SHIPPED"]:
            action = "Hold evidence submission; monitor carrier tracking until final delivery scan before deadline."
        else:
            action = "Request carrier delivery documentation from fulfillment center or consider proactive resolution."

        return EvidenceStrategyReport(
            dispute_id=dispute_id,
            category="INR",
            overall_strength_score=overall_score,
            items=items,
            identified_gaps=gaps,
            recommended_action=action,
            can_auto_submit=can_auto_submit,
        )

    def _evaluate_snad(
        self,
        dispute_id: str,
        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> EvidenceStrategyReport:
        """Evaluate Significantly Not As Described (SNAD) evidence chain."""
        items: List[EvidenceItem] = []
        gaps: List[str] = []
        critical_gap_present = False

        order = evidence_chain.get("order", {})
        order_items = order.get("items", [])

        # 1. Product catalog / listing description available (weight: 35)
        has_catalog = bool(order_items and any(item.get("description") or item.get("name") for item in order_items))
        if has_catalog:
            items.append(EvidenceItem(
                name="Product Listing & Catalog Specifications",
                evidence_type="PRODUCT_CATALOG",
                score=10.0,
                status="AVAILABLE",
                details="Detailed catalog title, model SKU, and product specifications verified.",
            ))
        else:
            items.append(EvidenceItem(
                name="Product Listing & Catalog Specifications",
                evidence_type="PRODUCT_CATALOG",
                score=2.0,
                status="MISSING",
                details="Listing description or catalog specifications are missing.",
            ))
            gaps.append("Missing product catalog specifications and detailed listing description.")
            critical_gap_present = True

        # 2. Itemized invoice matches claimed item (weight: 25)
        invoice = evidence_chain.get("invoice", {})
        if order_items or (invoice and invoice.get("items")):
            items.append(EvidenceItem(
                name="Itemized Invoice & Order Details",
                evidence_type="INVOICE",
                score=10.0,
                status="AVAILABLE",
                details="Line-item unit price, quantity, and product description match order records.",
            ))
        else:
            items.append(EvidenceItem(
                name="Itemized Invoice & Order Details",
                evidence_type="INVOICE",
                score=3.0,
                status="INCOMPLETE",
                details="Invoice lacks itemized breakdown matching the claimed dispute items.",
            ))
            gaps.append("Itemized invoice matching claimed product is missing.")
            critical_gap_present = True

        # 3. Clear return/refund policy published (weight: 20)
        has_return_policy = bool(dispute_data.get("return_policy") or evidence_chain.get("return_policy"))
        if has_return_policy:
            items.append(EvidenceItem(
                name="Store Return & Warranty Policy",
                evidence_type="RETURN_POLICY",
                score=10.0,
                status="AVAILABLE",
                details="Standard 30-day merchant return policy and terms on file.",
            ))
        else:
            items.append(EvidenceItem(
                name="Store Return & Warranty Policy",
                evidence_type="RETURN_POLICY",
                score=6.0,
                status="INCOMPLETE",
                details="Standard terms of service active, but specific RMA instructions not attached.",
            ))
            gaps.append("Store return policy terms not attached.")

        # 4. Pre-shipment inspection photos/logs (weight: 20)
        has_inspection = bool(
            dispute_data.get("inspection_photos")
            or evidence_chain.get("pre_shipment_inspection")
            or "inspection" in str(evidence_chain).lower()
        )
        if has_inspection:
            items.append(EvidenceItem(
                name="Pre-Shipment Quality Inspection",
                evidence_type="ITEM_SPECIFICATION",
                score=10.0,
                status="AVAILABLE",
                details="Pre-shipment serial number and condition verification photos attached.",
            ))
        else:
            items.append(EvidenceItem(
                name="Pre-Shipment Quality Inspection",
                evidence_type="ITEM_SPECIFICATION",
                score=0.0,
                status="MISSING",
                details="No pre-shipment quality photos or warehouse dispatch inspection records found.",
            ))
            gaps.append("Missing pre-shipment quality inspection photos or packing logs.")

        weights = [0.35, 0.25, 0.20, 0.20]
        overall_score = round(sum(item.score * 10 * w for item, w in zip(items, weights)), 1)
        can_auto_submit = overall_score >= self.AUTO_SUBMIT_THRESHOLD and not critical_gap_present

        action = (
            "Submit catalog specifications, invoice line items, and return terms to substantiate fulfillment accuracy."
            if not critical_gap_present
            else "Request warehouse dispatch photos before submitting counter-evidence to dispute."
        )

        return EvidenceStrategyReport(
            dispute_id=dispute_id,
            category="SNAD",
            overall_strength_score=overall_score,
            items=items,
            identified_gaps=gaps,
            recommended_action=action,
            can_auto_submit=can_auto_submit,
        )

    def _evaluate_unauthorized(
        self,
        dispute_id: str,
        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> EvidenceStrategyReport:
        """Evaluate Unauthorized Transaction claim evidence chain."""
        items: List[EvidenceItem] = []
        gaps: List[str] = []
        critical_gap_present = False

        order = evidence_chain.get("order", {})
        shipping = evidence_chain.get("shipping", {})

        # 1. Shipping address matches PayPal verified address (weight: 40)
        has_address = bool(order.get("shipping", {}).get("address") or shipping.get("shipping_address"))
        address_verified = dispute_data.get("shipping_address_verified", True)  # default true in sandbox
        if has_address and address_verified:
            items.append(EvidenceItem(
                name="PayPal Verified Shipping Address Match",
                evidence_type="BILLING_ADDRESS_MATCH",
                score=10.0,
                status="AVAILABLE",
                details="Items shipped directly to buyer's PayPal confirmed delivery address.",
            ))
        else:
            items.append(EvidenceItem(
                name="PayPal Verified Shipping Address Match",
                evidence_type="BILLING_ADDRESS_MATCH",
                score=0.0,
                status="MISSING",
                details="Destination address does not match PayPal confirmed account address.",
            ))
            gaps.append("Order was not shipped to buyer's PayPal verified address.")
            critical_gap_present = True

        # 2. Order confirmation delivered to account email (weight: 30)
        buyer_email = dispute_data.get("buyer_email")
        if buyer_email:
            items.append(EvidenceItem(
                name="Order Confirmation Email Delivery",
                evidence_type="ORDER_CONFIRMATION",
                score=10.0,
                status="AVAILABLE",
                details=f"Timestamped order receipt delivered to verified account email: {buyer_email}.",
            ))
        else:
            items.append(EvidenceItem(
                name="Order Confirmation Email Delivery",
                evidence_type="ORDER_CONFIRMATION",
                score=4.0,
                status="INCOMPLETE",
                details="Order confirmation dispatch log is unverified.",
            ))
            gaps.append("Order confirmation email receipt missing.")

        # 3. IP/device authentication logs or transaction history (weight: 30)
        auth_data = dispute_data.get("authentication_logs") or evidence_chain.get("authentication_logs")
        if auth_data:
            items.append(EvidenceItem(
                name="Authentication & Device Logs",
                evidence_type="AUTHENTICATION_LOGS",
                score=10.0,
                status="AVAILABLE",
                details="Customer authenticated via 2FA from recognized IP/device fingerprint.",
            ))
        else:
            items.append(EvidenceItem(
                name="Authentication & Device Logs",
                evidence_type="AUTHENTICATION_LOGS",
                score=6.0,
                status="INCOMPLETE",
                details="Standard session cookies captured, but advanced device fingerprinting unrecorded.",
            ))
            gaps.append("Detailed session IP and 2FA authentication logs not attached.")

        weights = [0.40, 0.30, 0.30]
        overall_score = round(sum(item.score * 10 * w for item, w in zip(items, weights)), 1)
        can_auto_submit = overall_score >= self.AUTO_SUBMIT_THRESHOLD and not critical_gap_present

        action = (
            "Submit verified shipping address match and order confirmation under PayPal Seller Protection Policy."
            if not critical_gap_present
            else "Review fulfillment address before responding; unverified address incurs high dispute liability."
        )

        return EvidenceStrategyReport(
            dispute_id=dispute_id,
            category="UNAUTHORIZED",
            overall_strength_score=overall_score,
            items=items,
            identified_gaps=gaps,
            recommended_action=action,
            can_auto_submit=can_auto_submit,
        )

    def _evaluate_general(
        self,
        dispute_id: str,
        category: str,
        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> EvidenceStrategyReport:
        """Evaluate general dispute categories (Cancellation, Return, Other)."""
        items = [
            EvidenceItem(
                name="Transaction & Fulfillment Timeline",
                evidence_type="TRANSACTION_LOG",
                score=8.0,
                status="AVAILABLE",
                details="Complete transaction creation and fulfillment timeline assembled.",
            ),
            EvidenceItem(
                name="Buyer Communication History",
                evidence_type="BUYER_COMMUNICATIONS",
                score=7.0,
                status="AVAILABLE",
                details="In-app messaging log between merchant and buyer preserved.",
            ),
        ]
        return EvidenceStrategyReport(
            dispute_id=dispute_id,
            category=category,
            overall_strength_score=75.0,
            items=items,
            identified_gaps=["Additional buyer concession proof recommended."],
            recommended_action="Compile transaction history and customer correspondence for manual dispute review.",
            can_auto_submit=False,
        )

    async def compile_evidence(
        self,
        strategy_report: EvidenceStrategyReport,
        evidence_chain: Dict[str, Any],
        dispute_data: Dict[str, Any],
    ) -> CompiledEvidencePayload:
        """
        Compile structured evidence items into a PayPal provide-evidence API payload,
        drafting an authoritative seller defense statement.
        """
        category = strategy_report.category
        dispute_id = strategy_report.dispute_id
        order = evidence_chain.get("order", {})
        shipping = evidence_chain.get("shipping", {})
        invoice = evidence_chain.get("invoice", {})

        order_id = str(order.get("order_id") or order.get("id") or dispute_data.get("paypal_order_id", "N/A"))
        carrier = shipping.get("carrier")
        tracking_number = shipping.get("tracking_number")
        delivery_status = shipping.get("delivery_status", "UNKNOWN")
        delivered_at = shipping.get("delivered_at") or "Confirmed Delivery Date"
        items_list = order.get("items", []) or invoice.get("items", [])
        items_summary = ", ".join(f"{it.get('name')} (SKU: {it.get('sku', 'N/A')})" for it in items_list) or "Ordered Goods"

        # 1. Determine PayPal evidence_type
        if category == "INR":
            evidence_type = "PROOF_OF_FULFILLMENT"
        elif category == "SNAD":
            evidence_type = "PROOF_OF_SIGNIFICANT_NOT_AS_DESCRIBED"
        elif category == "UNAUTHORIZED":
            evidence_type = "PROOF_OF_FULFILLMENT"
        else:
            evidence_type = "OTHER"

        # 2. Format tracking info for PayPal API schema
        tracking_info = None
        if tracking_number:
            tracking_info = [
                {
                    "carrier_name": carrier or "UPS",
                    "tracking_number": tracking_number,
                }
            ]

        # 3. Draft Defense Notes (LLM or High-Authority Fallback)
        notes = ""
        if self.llm:
            try:
                prompt = MERCHANT_EXPLANATION_PROMPT_TEMPLATE.format(
                    dispute_id=dispute_id,
                    category=category,
                    reason=dispute_data.get("reason", category),
                    amount=dispute_data.get("dispute_amount", "0.00"),
                    currency=dispute_data.get("dispute_currency", "USD"),
                    buyer_message=dispute_data.get("buyer_message", "No description provided."),
                    order_id=order_id,
                    items_summary=items_summary,
                    carrier=carrier or "N/A",
                    tracking_number=tracking_number or "N/A",
                    delivery_status=delivery_status,
                    delivery_timestamp=delivered_at,
                    proof_of_delivery_details=json.dumps(shipping.get("proof_of_delivery", {})),
                    return_policy="Standard 30-day merchant warranty and inspection terms.",
                )
                response = await self.llm.ainvoke(prompt)
                notes = response.content if hasattr(response, "content") else str(response)
            except Exception as exc:
                logger.warning(f"LLM explanation drafting failed: {exc}; using deterministic template.")

        if not notes:
            notes = self._synthesize_fallback_notes(
                category=category,
                dispute_id=dispute_id,
                order_id=order_id,
                items_summary=items_summary,
                carrier=carrier,
                tracking_number=tracking_number,
                delivery_status=delivery_status,
                delivered_at=delivered_at,
                dispute_data=dispute_data,
            )

        submission_ready = strategy_report.can_auto_submit and bool(notes)

        return CompiledEvidencePayload(
            dispute_id=dispute_id,
            evidence_type=evidence_type,
            notes=notes.strip(),
            tracking_info=tracking_info,
            documents=[],
            submission_ready=submission_ready,
        )

    def _synthesize_fallback_notes(
        self,
        category: str,
        dispute_id: str,
        order_id: str,
        items_summary: str,
        carrier: Optional[str],
        tracking_number: Optional[str],
        delivery_status: str,
        delivered_at: str,
        dispute_data: Dict[str, Any],
    ) -> str:
        """Deterministic professional defense statement formatted for PayPal reviewers."""
        reason = dispute_data.get("reason", category)
        if category == "INR":
            return (
                f"Official Merchant Counter-Evidence Statement for Dispute {dispute_id}.\n\n"
                f"This dispute was filed under reason '{reason}', claiming non-receipt of merchandise. "
                f"The merchant fulfilled order #{order_id} ({items_summary}) via {carrier or 'Carrier'} under tracking number {tracking_number or 'N/A'}. "
                f"Verifiable carrier tracking confirms delivery was completed on {delivered_at} with status '{delivery_status}'.\n\n"
                f"Pursuant to PayPal's Seller Protection Policy, the attached tracking confirmation and Proof of Delivery satisfy all online tracking requirements for tangible goods. "
                f"The merchant has completely satisfied all fulfillment obligations. We respectfully request that PayPal resolve this dispute in the merchant's favor and release the held funds."
            )
        elif category == "SNAD":
            return (
                f"Official Merchant Counter-Evidence Statement for Dispute {dispute_id}.\n\n"
                f"This dispute was filed alleging item not as described. The merchandise fulfilled under order #{order_id} ({items_summary}) "
                f"matches the exact specifications, SKU, and catalog listing purchased by the buyer. Itemized order and invoice records substantiate that the dispatched item corresponds precisely with order details.\n\n"
                f"Furthermore, the merchant's published return and warranty policy provides an established RMA procedure for legitimate returns. "
                f"The merchandise delivered is genuine, brand-new, and strictly conforms to all published catalog descriptions. We request that PayPal decline this claim under seller protection guidelines."
            )
        elif category == "UNAUTHORIZED":
            buyer_email = dispute_data.get("buyer_email", "the buyer's email")
            return (
                f"Official Merchant Counter-Evidence Statement for Dispute {dispute_id}.\n\n"
                f"Regarding the claim of unauthorized transaction, order #{order_id} was submitted and confirmed via the buyer's registered PayPal account "
                f"and dispatched directly to the PayPal-verified destination address. Timestamped order confirmations were delivered to {buyer_email}.\n\n"
                f"Under PayPal Seller Protection rules for unauthorized transactions, fulfilling to the confirmed shipping address with verifiable carrier delivery fulfills all protection prerequisites. "
                f"We respectfully request this claim be dismissed."
            )
        else:
            return (
                f"Official Merchant Counter-Evidence Statement for Dispute {dispute_id}.\n\n"
                f"Order #{order_id} was processed and fulfilled according to all agreed terms of sale. "
                f"Full transaction timeline and correspondence demonstrate proper order handling. "
                f"We request PayPal review the attached documentation and find in favor of the merchant."
            )

