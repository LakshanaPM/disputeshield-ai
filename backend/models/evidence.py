"""
DisputeShield AI — Evidence ORM Model

Represents a piece of evidence compiled by the AI agent for a dispute.
"""

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from database import Base


class EvidenceType(str, enum.Enum):
    """Types of evidence that can be submitted."""
    PROOF_OF_FULFILLMENT = "PROOF_OF_FULFILLMENT"
    PROOF_OF_DELIVERY = "PROOF_OF_DELIVERY"
    PROOF_OF_REFUND = "PROOF_OF_REFUND"
    PROOF_OF_DELIVERY_SIGNATURE = "PROOF_OF_DELIVERY_SIGNATURE"
    TRACKING_INFORMATION = "TRACKING_INFORMATION"
    PRODUCT_DESCRIPTION = "PRODUCT_DESCRIPTION"
    CUSTOMER_COMMUNICATION = "CUSTOMER_COMMUNICATION"
    RETURN_POLICY = "RETURN_POLICY"
    TERMS_AND_CONDITIONS = "TERMS_AND_CONDITIONS"
    INVOICE = "INVOICE"
    OTHER = "OTHER"


class EvidenceStatus(str, enum.Enum):
    """Status of evidence submission."""
    PENDING = "PENDING"
    COMPILED = "COMPILED"
    SUBMITTED = "SUBMITTED"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class Evidence(Base):
    """
    Evidence items compiled by the AI agent for dispute defense.
    Each dispute can have multiple evidence items.
    """
    __tablename__ = "evidence"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- Foreign Key ---
    dispute_id = Column(Integer, ForeignKey("disputes.id"), nullable=False, index=True)

    # --- Evidence Details ---
    evidence_type = Column(String(50), nullable=False)
    source = Column(String(50), nullable=True)  # e.g., "PayPal Orders API", "Shipment Tracking API"
    content = Column(Text, nullable=True)  # Raw evidence content / JSON payload
    notes = Column(Text, nullable=True)  # Agent-generated notes for this evidence
    file_url = Column(String(500), nullable=True)  # URL to evidence document if applicable

    # --- Scoring ---
    relevance_score = Column(Float, nullable=True)  # 0-10 relevance to dispute type
    strength_score = Column(Float, nullable=True)  # 0-10 how strong this evidence is

    # --- Status ---
    status = Column(String(50), nullable=False, default=EvidenceStatus.PENDING.value)

    # --- Timestamps ---
    compiled_at = Column(DateTime, nullable=True)
    submitted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    # --- Relationships ---
    dispute = relationship("Dispute", back_populates="evidence_items")

    def __repr__(self) -> str:
        return (
            f"<Evidence(id={self.id}, dispute_id={self.dispute_id}, "
            f"type='{self.evidence_type}', status='{self.status}')>"
        )
