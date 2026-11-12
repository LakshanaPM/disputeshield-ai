"""
DisputeShield AI — Demo Disputes Seeder (Day 14)

Populates the local database with a complete set of 20+ realistic dispute records,
associated merchant profile, linked evidence items, and RAG precedent metadata
for AG Grid SSRM and Recharts frontend integration.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault("DATABASE_URL", "sqlite:///./local_dev.db")

from database import SessionLocal, init_db
from models.dispute import Dispute, DisputeStatus, DisputeOutcome, AgentDecision
from models.merchant import Merchant
from models.evidence import Evidence, EvidenceStatus, EvidenceType

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def seed_database():
    """Seeds merchant, 20 diverse disputes, and associated evidence."""
    init_db()
    db = SessionLocal()
    try:
        now = datetime.utcnow()

        # -----------------------------------------------------------------
        # 1. Primary Demo Merchant
        # -----------------------------------------------------------------
        merchant = db.query(Merchant).filter(Merchant.paypal_merchant_id == "MERCHANT-DEMO-01").first()
        if not merchant:
            merchant = Merchant(
                paypal_merchant_id="MERCHANT-DEMO-01",
                business_name="DisputeShield Merchant Store",
                email="merchant@disputeshield.ai",
                dispute_ratio=0.88,
                account_health_score=82.5,
                risk_level="YELLOW",
                total_transactions_90d=2500,
                total_disputes_90d=22,
                total_disputes=20,
                disputes_won=18,
                disputes_lost=0,
                disputes_pending=2,
                win_rate=100.0,
                avg_response_time_minutes=4.2,
                money_saved=3240.50,
                auto_submit_threshold=80,
                draft_threshold=60,
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
            logger.info(f"Created primary merchant: {merchant.business_name} (ID: {merchant.id})")
        else:
            merchant.dispute_ratio = 0.88
            merchant.account_health_score = 82.5
            merchant.risk_level = "YELLOW"
            merchant.total_transactions_90d = 2500
            db.commit()
            logger.info(f"Updated primary merchant: {merchant.business_name} (ID: {merchant.id})")

        # -----------------------------------------------------------------
        # 2. Curated Dispute Records (20 Disputes)
        # -----------------------------------------------------------------
        disputes_data: List[Dict[str, Any]] = [
            # --- 8 INR Disputes ---
            # 5 AUTO_SUBMITTED with tracking & high confidence
            {
                "paypal_dispute_id": "PP-D-INR-1001",
                "paypal_order_id": "ORD-2026-9001",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 149.99,
                "dispute_currency": "USD",
                "buyer_email": "buyer1001@example.com",
                "buyer_message": "Package was never delivered to my apartment doorstep.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.88,
                "evidence_strength_score": 0.92,
                "agent_reasoning": "High confidence (88%). Proof of delivery verified via UPS tracking with postal code match and delivery photo. Automatically submitted to PayPal.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=6),
                "created_at": now - timedelta(days=2),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "UPS_TRACKING",
                    "tracking_info": [{"carrier_name": "UPS", "tracking_number": "1Z9999999999991001"}],
                    "notes": "Official Seller Defense: UPS Tracking 1Z9999999999991001 confirms delivery to front door on Oct 16. Recipient address matches PayPal order file exactly.",
                    "strength": 0.92,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-INR-1002",
                "paypal_order_id": "ORD-2026-9002",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 89.50,
                "dispute_currency": "USD",
                "buyer_email": "buyer1002@example.com",
                "buyer_message": "Tracking has not updated and item never arrived.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.86,
                "evidence_strength_score": 0.90,
                "agent_reasoning": "High confidence (86%). USPS Priority Mail tracking confirms delivery into recipient mailbox.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=5),
                "created_at": now - timedelta(days=3),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "USPS_TRACKING",
                    "tracking_info": [{"carrier_name": "USPS", "tracking_number": "94001118992231001002"}],
                    "notes": "USPS Priority delivery scan confirms item safely placed in mailbox on Oct 14.",
                    "strength": 0.90,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-INR-1003",
                "paypal_order_id": "ORD-2026-9003",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 320.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1003@example.com",
                "buyer_message": "High value order never arrived at business office.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.92,
                "evidence_strength_score": 0.95,
                "agent_reasoning": "Very high confidence (92%). FedEx Direct Signature obtained from front desk manager.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=4),
                "created_at": now - timedelta(days=4),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "FEDEX_TRACKING",
                    "tracking_info": [{"carrier_name": "FedEx", "tracking_number": "794892831003"}],
                    "notes": "FedEx Direct Signature confirmation obtained at reception desk. Recipient signature on file.",
                    "strength": 0.95,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-INR-1004",
                "paypal_order_id": "ORD-2026-9004",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 45.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1004@example.com",
                "buyer_message": "Did not receive digital software license key.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.84,
                "evidence_strength_score": 0.88,
                "agent_reasoning": "High confidence (84%). Server authentication logs verify license key was activated and accessed.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=7),
                "created_at": now - timedelta(days=1),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_FULFILLMENT.value,
                    "source": "LICENSE_SERVER",
                    "tracking_info": [],
                    "notes": "Digital license key delivered to buyer email and activated from IP matching checkout session.",
                    "strength": 0.88,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-INR-1005",
                "paypal_order_id": "ORD-2026-9005",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 195.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1005@example.com",
                "buyer_message": "Package was supposedly left on porch but cannot find it.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.85,
                "evidence_strength_score": 0.89,
                "agent_reasoning": "High confidence (85%). Carrier geo-coordinates and front porch photo match buyer address.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=6),
                "created_at": now - timedelta(days=2),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "UPS_TRACKING",
                    "tracking_info": [{"carrier_name": "UPS", "tracking_number": "1Z9999999999991005"}],
                    "notes": "Carrier delivery verification with geo-stamped delivery photograph matching residence entryway.",
                    "strength": 0.89,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            # 2 DRAFT_PENDING_REVIEW (awaiting merchant 1-click review)
            {
                "paypal_dispute_id": "PP-D-INR-1006",
                "paypal_order_id": "ORD-2026-9006",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.WAITING_FOR_SELLER_RESPONSE.value,
                "dispute_amount": 110.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1006@example.com",
                "buyer_message": "Tracking shows package in transit for 10 days without movement.",
                "agent_decision": AgentDecision.DRAFT_PENDING_REVIEW.value,
                "confidence_score": 0.68,
                "evidence_strength_score": 0.65,
                "agent_reasoning": "Moderate confidence (68%). Carrier tracking in transit; final delivery scan missing. Drafted seller explanation for merchant review.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=3),
                "created_at": now - timedelta(days=5),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [{"carrier_name": "USPS", "tracking_number": "94001118992231001006"}],
                    "notes": "Draft Defense: Package shipped on time via USPS Priority. Severe weather in destination region delayed final delivery scan.",
                    "strength": 0.65,
                    "status": EvidenceStatus.COMPILED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-INR-1007",
                "paypal_order_id": "ORD-2026-9007",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.WAITING_FOR_SELLER_RESPONSE.value,
                "dispute_amount": 75.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1007@example.com",
                "buyer_message": "Driver marked delivered but building concierge says nothing arrived.",
                "agent_decision": AgentDecision.DRAFT_PENDING_REVIEW.value,
                "confidence_score": 0.72,
                "evidence_strength_score": 0.74,
                "agent_reasoning": "Moderate confidence (72%). Carrier marked delivered to mailroom. Merchant verification recommended.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=4),
                "created_at": now - timedelta(days=3),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [{"carrier_name": "FedEx", "tracking_number": "794892831007"}],
                    "notes": "Draft Defense: FedEx tracking shows delivered to building mailroom. Building staff signature obtained.",
                    "strength": 0.74,
                    "status": EvidenceStatus.COMPILED.value,
                },
            },
            # 1 ESCALATED
            {
                "paypal_dispute_id": "PP-D-INR-1008",
                "paypal_order_id": "ORD-2026-9008",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.OPEN.value,
                "dispute_amount": 480.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer1008@example.com",
                "buyer_message": "International shipment lost in customs. Demanding full refund immediately.",
                "agent_decision": AgentDecision.ESCALATED.value,
                "confidence_score": 0.42,
                "evidence_strength_score": 0.40,
                "agent_reasoning": "Low confidence (42%). International customs clearance delay with missing commercial invoice. Escalated for human resolution.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=2),
                "created_at": now - timedelta(days=6),
                "evidence": {
                    "type": EvidenceType.OTHER.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [{"carrier_name": "DHL", "tracking_number": "DHL98231008"}],
                    "notes": "Critical Defense Gap: International tracking status 'Held in Customs'. Awaiting merchant customs clearance documentation.",
                    "strength": 0.40,
                    "status": EvidenceStatus.PENDING.value,
                },
            },

            # --- 6 SNAD Disputes ---
            # 3 WON
            {
                "paypal_dispute_id": "PP-D-SNAD-2001",
                "paypal_order_id": "ORD-2026-9009",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.RESOLVED.value,
                "dispute_amount": 185.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2001@example.com",
                "buyer_message": "Lens specifications mismatch listing.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.86,
                "evidence_strength_score": 0.90,
                "agent_reasoning": "Resolution in merchant favor. SKU code and manufacturer specification matched order invoice exactly.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.WON.value,
                "created_at": now - timedelta(days=25),
                "evidence": {
                    "type": EvidenceType.PRODUCT_DESCRIPTION.value,
                    "source": "CATALOG_SPEC_SHEET",
                    "tracking_info": [],
                    "notes": "Manufacturer spec sheet and product catalog snapshot verify exact SKU delivered.",
                    "strength": 0.90,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-SNAD-2002",
                "paypal_order_id": "ORD-2026-9010",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.RESOLVED.value,
                "dispute_amount": 95.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2002@example.com",
                "buyer_message": "Leather color shade looks lighter than photos.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.82,
                "evidence_strength_score": 0.85,
                "agent_reasoning": "Resolution in merchant favor. Listing prominently featured natural leather color variance disclaimer.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.WON.value,
                "created_at": now - timedelta(days=20),
                "evidence": {
                    "type": EvidenceType.PRODUCT_DESCRIPTION.value,
                    "source": "TERMS_AND_CONDITIONS",
                    "tracking_info": [],
                    "notes": "Product listing disclaimer explicitly described natural leather color grain variances.",
                    "strength": 0.85,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-SNAD-2003",
                "paypal_order_id": "ORD-2026-9011",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.RESOLVED.value,
                "dispute_amount": 125.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2003@example.com",
                "buyer_message": "Jacket sizing is too small.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.80,
                "evidence_strength_score": 0.84,
                "agent_reasoning": "Resolution in merchant favor. Accurate dimensional sizing chart provided; return policy upheld.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.WON.value,
                "created_at": now - timedelta(days=16),
                "evidence": {
                    "type": EvidenceType.PRODUCT_DESCRIPTION.value,
                    "source": "SIZING_CHART",
                    "tracking_info": [],
                    "notes": "Garment dimensional sizing chart matches factory tag measurements exactly.",
                    "strength": 0.84,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            # 2 DRAFT_PENDING_REVIEW
            {
                "paypal_dispute_id": "PP-D-SNAD-2004",
                "paypal_order_id": "ORD-2026-9012",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.WAITING_FOR_SELLER_RESPONSE.value,
                "dispute_amount": 210.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2004@example.com",
                "buyer_message": "Headphones microphone does not function properly on Windows.",
                "agent_decision": AgentDecision.DRAFT_PENDING_REVIEW.value,
                "confidence_score": 0.65,
                "evidence_strength_score": 0.70,
                "agent_reasoning": "Moderate confidence (65%). Requires driver setup; draft defense prepared with return shipping label offer.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=5),
                "created_at": now - timedelta(days=2),
                "evidence": {
                    "type": EvidenceType.PRODUCT_DESCRIPTION.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [],
                    "notes": "Draft Defense: Device requires firmware update per user manual. Pre-paid replacement label offered to buyer.",
                    "strength": 0.70,
                    "status": EvidenceStatus.COMPILED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-SNAD-2005",
                "paypal_order_id": "ORD-2026-9013",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.WAITING_FOR_SELLER_RESPONSE.value,
                "dispute_amount": 160.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2005@example.com",
                "buyer_message": "Ordered ceramic bowl set, arrived with chip on edge.",
                "agent_decision": AgentDecision.DRAFT_PENDING_REVIEW.value,
                "confidence_score": 0.62,
                "evidence_strength_score": 0.60,
                "agent_reasoning": "Moderate confidence (62%). Buyer claims transit damage. Merchant should review parcel insurance coverage.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=4),
                "created_at": now - timedelta(days=3),
                "evidence": {
                    "type": EvidenceType.OTHER.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [],
                    "notes": "Draft Defense: Package was insured with bubble-wrap packaging. Partial refund or replacement bowl offer prepared.",
                    "strength": 0.60,
                    "status": EvidenceStatus.COMPILED.value,
                },
            },
            # 1 ESCALATED
            {
                "paypal_dispute_id": "PP-D-SNAD-2006",
                "paypal_order_id": "ORD-2026-9014",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.OPEN.value,
                "dispute_amount": 620.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer2006@example.com",
                "buyer_message": "Vintage watch is alleged counterfeit by third-party jeweler.",
                "agent_decision": AgentDecision.ESCALATED.value,
                "confidence_score": 0.35,
                "evidence_strength_score": 0.38,
                "agent_reasoning": "High dispute amount ($620) and authenticity challenge. Escalated for human certification upload.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=3),
                "created_at": now - timedelta(days=4),
                "evidence": {
                    "type": EvidenceType.OTHER.value,
                    "source": "DISPUTESHIELD_AI",
                    "tracking_info": [],
                    "notes": "Escalated Defense: Independent horologist certificate of authenticity required to refute counterfeit allegation.",
                    "strength": 0.38,
                    "status": EvidenceStatus.PENDING.value,
                },
            },

            # --- 4 Unauthorized Disputes ---
            # 3 AUTO_SUBMITTED
            {
                "paypal_dispute_id": "PP-D-UNAUTH-3001",
                "paypal_order_id": "ORD-2026-9015",
                "reason": "UNAUTHORIZED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 110.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer3001@example.com",
                "buyer_message": "Unrecognized charge on my PayPal credit statement.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.91,
                "evidence_strength_score": 0.94,
                "agent_reasoning": "High confidence (91%). Shipped directly to confirmed PayPal address with AVS match and 2FA authentication timestamp.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=6),
                "created_at": now - timedelta(days=1),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "PAYPAL_AVS_CHECK",
                    "tracking_info": [{"carrier_name": "UPS", "tracking_number": "1Z9999999999993001"}],
                    "notes": "Delivered to verified PayPal account holder billing address with full AVS/CVV match. Eligible for Seller Protection.",
                    "strength": 0.94,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-UNAUTH-3002",
                "paypal_order_id": "ORD-2026-9016",
                "reason": "UNAUTHORIZED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 65.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer3002@example.com",
                "buyer_message": "Unauthorized transaction for digital gaming credits.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.88,
                "evidence_strength_score": 0.90,
                "agent_reasoning": "High confidence (88%). Device fingerprint and session IP matched established customer account history.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=5),
                "created_at": now - timedelta(days=2),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_FULFILLMENT.value,
                    "source": "ACCOUNT_SESSION_LOGS",
                    "tracking_info": [],
                    "notes": "Transaction initiated from habitual device fingerprint with 2-year customer transaction history.",
                    "strength": 0.90,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-UNAUTH-3003",
                "paypal_order_id": "ORD-2026-9017",
                "reason": "UNAUTHORIZED",
                "status": DisputeStatus.UNDER_REVIEW.value,
                "dispute_amount": 240.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer3003@example.com",
                "buyer_message": "Did not approve purchase of electronic accessories.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.87,
                "evidence_strength_score": 0.91,
                "agent_reasoning": "High confidence (87%). Delivered to verified address with FedEx adult signature on file.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=7),
                "created_at": now - timedelta(days=1),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "FEDEX_TRACKING",
                    "tracking_info": [{"carrier_name": "FedEx", "tracking_number": "794892833003"}],
                    "notes": "FedEx delivery receipt with signature matching registered PayPal account holder.",
                    "strength": 0.91,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            # 1 DRAFT_PENDING_REVIEW
            {
                "paypal_dispute_id": "PP-D-UNAUTH-3004",
                "paypal_order_id": "ORD-2026-9018",
                "reason": "UNAUTHORIZED",
                "status": DisputeStatus.WAITING_FOR_SELLER_RESPONSE.value,
                "dispute_amount": 80.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer3004@example.com",
                "buyer_message": "Disputing annual recurring SaaS subscription renewal.",
                "agent_decision": AgentDecision.DRAFT_PENDING_REVIEW.value,
                "confidence_score": 0.74,
                "evidence_strength_score": 0.76,
                "agent_reasoning": "Moderate confidence (74%). PayPal recurring billing agreement ID on file. Prepared renewal statement for merchant approval.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.PENDING.value,
                "response_deadline": now + timedelta(days=4),
                "created_at": now - timedelta(days=3),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_FULFILLMENT.value,
                    "source": "BILLING_AGREEMENT",
                    "tracking_info": [],
                    "notes": "Draft Defense: Buyer executed PayPal Billing Agreement B-9018. Advance reminder email dispatched 7 days prior.",
                    "strength": 0.76,
                    "status": EvidenceStatus.COMPILED.value,
                },
            },

            # --- 2 Resolved Historical Disputes ---
            {
                "paypal_dispute_id": "PP-D-RESOLVED-4001",
                "paypal_order_id": "ORD-2026-9019",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": DisputeStatus.RESOLVED.value,
                "dispute_amount": 175.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer4001@example.com",
                "buyer_message": "Claimed item never arrived.",
                "agent_decision": AgentDecision.AUTO_SUBMITTED.value,
                "confidence_score": 0.93,
                "evidence_strength_score": 0.96,
                "agent_reasoning": "Dispute successfully won. UPS proof of delivery fully accepted by PayPal.",
                "evidence_submitted": True,
                "outcome": DisputeOutcome.WON.value,
                "created_at": now - timedelta(days=40),
                "evidence": {
                    "type": EvidenceType.PROOF_OF_DELIVERY.value,
                    "source": "UPS_TRACKING",
                    "tracking_info": [{"carrier_name": "UPS", "tracking_number": "1Z9999999999994001"}],
                    "notes": "UPS proof of delivery accepted by PayPal review committee. Funds released to merchant.",
                    "strength": 0.96,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
            {
                "paypal_dispute_id": "PP-D-RESOLVED-4002",
                "paypal_order_id": "ORD-2026-9020",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                "status": DisputeStatus.RESOLVED.value,
                "dispute_amount": 290.00,
                "dispute_currency": "USD",
                "buyer_email": "buyer4002@example.com",
                "buyer_message": "Item arrived broken in half.",
                "agent_decision": AgentDecision.ACCEPTED_CLAIM.value,
                "confidence_score": 0.45,
                "evidence_strength_score": 0.42,
                "agent_reasoning": "Auto-concession triage applied: Carrier transit damage verified. Proactive claim accepted to eliminate $20 dispute fee and guarantee 100% defended win rate.",
                "evidence_submitted": False,
                "outcome": DisputeOutcome.SETTLED.value,
                "created_at": now - timedelta(days=38),
                "evidence": {
                    "type": EvidenceType.OTHER.value,
                    "source": "MERCHANT_SUBMISSION",
                    "tracking_info": [],
                    "notes": "Proactive claim settlement via PayPal API; avoided chargeback arbitration fee and preserved 100% contested win rate.",
                    "strength": 0.42,
                    "status": EvidenceStatus.SUBMITTED.value,
                },
            },
        ]

        seeded_count = 0
        for item in disputes_data:
            existing = db.query(Dispute).filter(Dispute.paypal_dispute_id == item["paypal_dispute_id"]).first()
            if not existing:
                dispute = Dispute(
                    paypal_dispute_id=item["paypal_dispute_id"],
                    paypal_order_id=item["paypal_order_id"],
                    reason=item["reason"],
                    status=item["status"],
                    dispute_amount=item["dispute_amount"],
                    dispute_currency=item["dispute_currency"],
                    buyer_email=item["buyer_email"],
                    buyer_message=item["buyer_message"],
                    agent_decision=item["agent_decision"],
                    confidence_score=item["confidence_score"],
                    evidence_strength_score=item["evidence_strength_score"],
                    agent_reasoning=item["agent_reasoning"],
                    evidence_submitted=item["evidence_submitted"],
                    outcome=item["outcome"],
                    response_deadline=item.get("response_deadline"),
                    agent_processed_at=item["created_at"] + timedelta(minutes=5),
                    evidence_submitted_at=item["created_at"] + timedelta(minutes=6) if item["evidence_submitted"] else None,
                    created_at=item["created_at"],
                    merchant_id=merchant.id,
                    seller_merchant_id=merchant.paypal_merchant_id,
                    similar_cases_json=json.dumps([
                        {"dispute_id": "PRECEDENT-DEMO-01", "outcome": "WON", "similarity": 0.94},
                        {"dispute_id": "PRECEDENT-DEMO-02", "outcome": "WON", "similarity": 0.91},
                    ]),
                )
                db.add(dispute)
                db.flush()

                # Add linked evidence record
                ev_data = item["evidence"]
                evidence_record = Evidence(
                    dispute_id=dispute.id,
                    evidence_type=ev_data["type"],
                    source=ev_data["source"],
                    content=json.dumps({"tracking_info": ev_data.get("tracking_info", [])}),
                    notes=ev_data["notes"],
                    strength_score=ev_data["strength"],
                    status=ev_data["status"],
                    compiled_at=item["created_at"] + timedelta(minutes=5),
                    submitted_at=item["created_at"] + timedelta(minutes=6) if item["evidence_submitted"] else None,
                )
                db.add(evidence_record)
                seeded_count += 1
            else:
                # Update status
                existing.status = item["status"]
                existing.agent_decision = item["agent_decision"]
                existing.confidence_score = item["confidence_score"]
                existing.evidence_strength_score = item["evidence_strength_score"]
                existing.outcome = item["outcome"]
                seeded_count += 1

        db.commit()
        logger.info(f"Successfully seeded {seeded_count} realistic demo disputes for frontend master-detail dashboard.")

        print("\n" + "=" * 65)
        print("   DISPUTESHIELD AI — DATABASE DEMO SEEDING COMPLETE")
        print("=" * 65)
        print(f"Merchant               : {merchant.business_name} ({merchant.paypal_merchant_id})")
        print(f"90-Day Dispute Ratio   : {merchant.dispute_ratio}% ({merchant.risk_level} Risk Tier)")
        print(f"Total Disputes Seeded  : {seeded_count}")
        print(" - AUTO_SUBMITTED      : 11 disputes (Ready for PayPal evaluation)")
        print(" - DRAFT_PENDING_REVIEW: 5 disputes (Ready for 1-click merchant review)")
        print(" - ESCALATED           : 2 disputes (Flagged for human investigation)")
        print(" - RESOLVED            : 2 disputes (Historical Won/Lost precedents)")
        print("=" * 65 + "\n")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
