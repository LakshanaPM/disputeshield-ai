"""
DisputeShield AI — Dispute Pydantic Schemas

Request/response schemas for the disputes API endpoints.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# --- Response Schemas ---

class EvidenceItemResponse(BaseModel):
    """Single evidence item in a dispute response."""
    id: int
    evidence_type: str
    source: Optional[str] = None
    notes: Optional[str] = None
    relevance_score: Optional[float] = None
    strength_score: Optional[float] = None
    status: str
    compiled_at: Optional[datetime] = None
    submitted_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class MerchantInfoResponse(BaseModel):
    """Merchant profile details embedded in dispute responses."""
    id: int
    paypal_merchant_id: str
    business_name: Optional[str] = None
    email: Optional[str] = None
    dispute_ratio: float = 0.0
    account_health_score: float = 100.0
    risk_level: str = "GREEN"

    model_config = {"from_attributes": True}


class DisputeResponse(BaseModel):
    """Full dispute response for detail views."""
    id: int
    paypal_dispute_id: str
    paypal_order_id: Optional[str] = None
    paypal_transaction_id: Optional[str] = None
    reason: str
    status: str
    dispute_amount: float
    dispute_currency: str
    dispute_life_cycle_stage: Optional[str] = None
    buyer_email: Optional[str] = None
    seller_merchant_id: Optional[str] = None
    merchant_id: Optional[int] = None
    buyer_message: Optional[str] = None
    seller_response: Optional[str] = None
    agent_decision: str
    confidence_score: Optional[float] = None
    agent_reasoning: Optional[str] = None
    evidence_submitted: bool
    evidence_strength_score: Optional[float] = None
    outcome: str
    response_deadline: Optional[datetime] = None
    agent_processed_at: Optional[datetime] = None
    evidence_submitted_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    evidence_items: List[EvidenceItemResponse] = []
    merchant: Optional[MerchantInfoResponse] = None

    model_config = {"from_attributes": True}


class DisputeListItem(BaseModel):
    """Compact dispute for grid/list views."""
    id: int
    paypal_dispute_id: str
    reason: str
    status: str
    dispute_amount: float
    dispute_currency: str
    agent_decision: str
    confidence_score: Optional[float] = None
    evidence_submitted: bool
    outcome: str
    response_deadline: Optional[datetime] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class DisputeListResponse(BaseModel):
    """AG Grid Server-Side Row Model (SSRM) response structure."""
    rows: List[DisputeListItem]
    total_count: int
    start_row: int
    end_row: int


# --- Request Schemas ---

class DisputeApproveRequest(BaseModel):
    """Merchant approves agent's evidence draft."""
    approved: bool = True
    modifications: Optional[str] = None  # Optional modifications to evidence


class DisputeOverrideRequest(BaseModel):
    """Merchant overrides agent's evidence with custom content."""
    evidence_notes: str
    additional_context: Optional[str] = None
