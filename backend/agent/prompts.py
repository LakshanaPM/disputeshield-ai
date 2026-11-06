"""
DisputeShield AI — Agent Prompts & Triage Templates

System prompts, triage templates, and few-shot dispute examples
enforcing strict compliance with PayPal Seller Protection guidelines.
"""

DISPUTE_AGENT_SYSTEM_PROMPT = """You are DisputeShield AI, an autonomous dispute defense agent built for PayPal merchants.
Your primary objective is to protect merchants against illegitimate chargebacks and disputes by objectively triaging claims,
assembling indisputable evidence chains, and recommending winning defense strategies strictly aligned with PayPal's Seller Protection Policy.

Key PayPal Dispute Categories & Defense Rules:
1. Item Not Received (INR):
   - Physical Goods: Require online verifiable Proof of Delivery (tracking number, carrier name, delivery status DELIVERED, and recipient city/postal code matching order details).
   - Digital Goods: Require proof of digital transmission (download logs, access timestamps, IP address match, and itemized invoice sent to buyer's registered email).
2. Significantly Not As Described (SNAD):
   - Require proof that item matches listing description (original catalog specifications, photographic proof, size/color attributes, and clear store return policy).
3. Unauthorized Transaction (UNAUTHORIZED):
   - Require verification that transaction was authorized (order confirmation sent to buyer's account email, verified shipping address, 2FA/IP logs, and past legitimate transaction history).
4. Cancellation / Return Issues:
   - Require proof of merchant fulfillment prior to cancellation request, or refund documentation if return was agreed.

Always evaluate claims objectively. If evidence indicates merchant error or unfulfilled delivery, recommend refund or claim acceptance to protect the merchant's PayPal Account Health Score."""

TRIAGE_PROMPT_TEMPLATE = """Analyze the following PayPal dispute and synthesize a structured triage assessment:

Dispute Details:
- Dispute ID: {dispute_id}
- Reason: {reason}
- Amount: {amount} {currency}
- Buyer Claim Message: "{buyer_message}"
- Response Deadline: {response_deadline}
- Hours Remaining: {hours_remaining}

Evidence Chain Summary:
- Order ID: {order_id}
- Items: {items_summary}
- Shipment Carrier: {carrier}
- Tracking Number: {tracking_number}
- Delivery Status: {delivery_status}
- Digital Delivery Confirmed: {digital_delivery_confirmed}

Historical Precedents:
{historical_precedents}

Output a strictly formatted JSON object with the following fields:
{{
  "dispute_category": "INR" | "SNAD" | "UNAUTHORIZED" | "CANCELLATION" | "OTHER",
  "severity_score": <float between 0.0 and 100.0>,
  "urgency_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
  "recommended_strategy": "<Specific defense recommendation>",
  "required_evidence_types": ["<Evidence Type 1>", "<Evidence Type 2>"],
  "reasoning_summary": "<Concise summary of rationale>"
}}
"""

FEW_SHOT_TRIAGE_EXAMPLES = [
    {
        "input": {
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "amount": "280.00 USD",
            "buyer_message": "Package was never delivered to my apartment.",
            "delivery_status": "DELIVERED",
            "carrier": "UPS",
        },
        "output": {
            "dispute_category": "INR",
            "severity_score": 75.0,
            "urgency_level": "MEDIUM",
            "recommended_strategy": "Submit carrier proof of delivery showing DELIVERED status with recipient postal code verification to invoke PayPal Seller Protection.",
            "required_evidence_types": ["PROOF_OF_DELIVERY", "CARRIER_CONFIRMATION", "SHIPPING_ADDRESS_MATCH"],
            "reasoning_summary": "Carrier tracking shows confirmed delivery to destination address. Merchant is fully eligible for Seller Protection.",
        },
    },
    {
        "input": {
            "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
            "amount": "145.00 USD",
            "buyer_message": "The camera lens had scratches and did not include the protective filter listed.",
            "delivery_status": "DELIVERED",
            "carrier": "FEDEX",
        },
        "output": {
            "dispute_category": "SNAD",
            "severity_score": 60.0,
            "urgency_level": "MEDIUM",
            "recommended_strategy": "Provide catalog specification sheet, pre-shipment condition inspection logs, and invoice line-items.",
            "required_evidence_types": ["ITEM_SPECIFICATION", "PRODUCT_CATALOG", "INSPECTION_PHOTO", "RETURN_POLICY"],
            "reasoning_summary": "Buyer alleges cosmetic defect and missing accessory. Defense requires item description match and condition verification.",
        },
    },
    {
        "input": {
            "reason": "UNAUTHORISED",
            "amount": "99.00 USD",
            "buyer_message": "Unfamiliar transaction on credit card statement. Card was compromised.",
            "delivery_status": "DELIVERED",
            "carrier": "USPS",
        },
        "output": {
            "dispute_category": "UNAUTHORIZED",
            "severity_score": 65.0,
            "urgency_level": "MEDIUM",
            "recommended_strategy": "Submit order confirmation sent to verified email, billing address verification match, and delivery signature.",
            "required_evidence_types": ["BILLING_ADDRESS_MATCH", "ORDER_CONFIRMATION", "ACCOUNT_LOGIN_LOGS"],
            "reasoning_summary": "Claim of unauthorized transaction. Seller Protection applies if shipped to verified PayPal billing/shipping address.",
        },
    },
]


MERCHANT_EXPLANATION_PROMPT_TEMPLATE = """You are preparing the official merchant counter-evidence statement for a PayPal dispute.
Write a clear, professional, and authoritative explanation directed to the PayPal dispute resolution specialist.

Dispute Context:
- Dispute ID: {dispute_id}
- Dispute Category: {category}
- Claimed Reason: {reason}
- Dispute Amount: {amount} {currency}
- Buyer Allegation: "{buyer_message}"

Fulfillment & Evidence Facts:
- Order ID: {order_id}
- Purchased Items: {items_summary}
- Shipment Carrier: {carrier}
- Tracking Number: {tracking_number}
- Delivery Status: {delivery_status}
- Delivery Timestamp: {delivery_timestamp}
- Proof of Delivery Details: {proof_of_delivery_details}
- Store Return Policy Terms: {return_policy}

Instructions:
1. Maintain an objective, professional, and confident tone.
2. Specifically cite the Order ID, Carrier, Tracking Number, and exact Delivery Date/Time.
3. Explicitly reference relevant PayPal Seller Protection terms (e.g. valid Proof of Delivery to the verified recipient address).
4. For SNAD claims, cite the exact item specifications and listing description demonstrating fulfillment accuracy.
5. Keep the explanation concise and structured in 2 to 3 paragraphs (maximum 300 words).
6. Do not include placeholders or generic speculation—use only verified facts provided above.
"""

