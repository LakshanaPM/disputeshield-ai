"""
DisputeShield AI — Dispute ORM Model

Represents a PayPal dispute tracked by the system.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, Enum as SQLEnum, Boolean, ForeignKey
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum

from database import Base


class DisputeStatus(str, enum.Enum):
    """Dispute lifecycle status."""
    OPEN = "OPEN"
    WAITING_FOR_BUYER_RESPONSE = "WAITING_FOR_BUYER_RESPONSE"
    WAITING_FOR_SELLER_RESPONSE = "WAITING_FOR_SELLER_RESPONSE"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESOLVED = "RESOLVED"
    OTHER = "OTHER"


class DisputeReason(str, enum.Enum):
    """PayPal dispute reason codes."""
    MERCHANDISE_OR_SERVICE_NOT_RECEIVED = "MERCHANDISE_OR_SERVICE_NOT_RECEIVED"
    MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED = "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED"
    UNAUTHORIZED = "UNAUTHORIZED"
    CREDIT_NOT_PROCESSED = "CREDIT_NOT_PROCESSED"
    DUPLICATE_TRANSACTION = "DUPLICATE_TRANSACTION"
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    PAYMENT_BY_OTHER_MEANS = "PAYMENT_BY_OTHER_MEANS"
    OTHER = "OTHER"


class AgentDecision(str, enum.Enum):
    """The AI agent's decision for this dispute."""
    AUTO_SUBMITTED = "AUTO_SUBMITTED"
    DRAFT_PENDING_REVIEW = "DRAFT_PENDING_REVIEW"
    ESCALATED_TO_MERCHANT = "ESCALATED_TO_MERCHANT"
    ESCALATED = "ESCALATED"
    ESCALATE_TO_HUMAN = "ESCALATE_TO_HUMAN"
    ACCEPTED_CLAIM = "ACCEPTED_CLAIM"
    APPEALED = "APPEALED"
    PENDING = "PENDING"



class DisputeOutcome(str, enum.Enum):
    """Final outcome of the dispute."""
    WON = "WON"
    LOST = "LOST"
    SETTLED = "SETTLED"
    WITHDRAWN = "WITHDRAWN"
    PENDING = "PENDING"


class Dispute(Base):
    """
    Core dispute model tracking PayPal disputes and agent actions.
    """
    __tablename__ = "disputes"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- PayPal Identifiers ---
    paypal_dispute_id = Column(String(50), unique=True, nullable=False, index=True)
    paypal_order_id = Column(String(50), nullable=True)
    paypal_transaction_id = Column(String(50), nullable=True)

    # --- Dispute Details ---
    reason = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default=DisputeStatus.OPEN.value)
    dispute_amount = Column(Float, nullable=False, default=0.0)
    dispute_currency = Column(String(10), nullable=False, default="USD")
    dispute_life_cycle_stage = Column(String(50), nullable=True)

    # --- Parties ---
    buyer_email = Column(String(255), nullable=True)
    seller_merchant_id = Column(String(100), nullable=True)
    merchant_id = Column(Integer, ForeignKey("merchants.id"), nullable=True, index=True)

    # --- Messages & Context ---
    buyer_message = Column(Text, nullable=True)
    seller_response = Column(Text, nullable=True)

    # --- Agent Processing ---
    agent_decision = Column(String(50), nullable=False, default=AgentDecision.PENDING.value)
    confidence_score = Column(Float, nullable=True)
    agent_reasoning = Column(Text, nullable=True)
    evidence_submitted = Column(Boolean, default=False)
    evidence_strength_score = Column(Float, nullable=True)

    # --- Outcome ---
    outcome = Column(String(50), nullable=False, default=DisputeOutcome.PENDING.value)

    # --- RAG ---
    similar_cases_json = Column(Text, nullable=True)  # JSON string of similar past cases

    # --- Timestamps ---
    paypal_create_time = Column(DateTime, nullable=True)
    paypal_update_time = Column(DateTime, nullable=True)
    response_deadline = Column(DateTime, nullable=True)
    agent_processed_at = Column(DateTime, nullable=True)
    evidence_submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # --- Relationships ---
    merchant = relationship("Merchant", back_populates="disputes")
    evidence_items = relationship("Evidence", back_populates="dispute", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return (
            f"<Dispute(id={self.id}, paypal_id='{self.paypal_dispute_id}', "
            f"reason='{self.reason}', status='{self.status}', "
            f"amount={self.dispute_amount} {self.dispute_currency})>"
        )
