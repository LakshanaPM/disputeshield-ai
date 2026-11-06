"""
DisputeShield AI — Merchant ORM Model

Represents a PayPal merchant using DisputeShield.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class Merchant(Base):
    """
    Merchant profile with account health metrics and dispute statistics.
    """
    __tablename__ = "merchants"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- PayPal Identifiers ---
    paypal_merchant_id = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), nullable=True)
    business_name = Column(String(255), nullable=True)

    # --- Account Health ---
    dispute_ratio = Column(Float, nullable=False, default=0.0)  # Current dispute ratio (%)
    account_health_score = Column(Float, nullable=False, default=100.0)  # 0-100 health score
    risk_level = Column(String(20), nullable=False, default="GREEN")  # GREEN/YELLOW/ORANGE/RED
    total_transactions_90d = Column(Integer, nullable=False, default=0)
    total_disputes_90d = Column(Integer, nullable=False, default=0)

    # --- Dispute Stats ---
    total_disputes = Column(Integer, nullable=False, default=0)
    disputes_won = Column(Integer, nullable=False, default=0)
    disputes_lost = Column(Integer, nullable=False, default=0)
    disputes_pending = Column(Integer, nullable=False, default=0)
    win_rate = Column(Float, nullable=False, default=0.0)
    avg_response_time_minutes = Column(Float, nullable=True)
    money_saved = Column(Float, nullable=False, default=0.0)  # Total dispute amount won back

    # --- Agent Preferences ---
    auto_submit_threshold = Column(Integer, nullable=False, default=80)
    draft_threshold = Column(Integer, nullable=False, default=60)

    # --- Relationships ---
    disputes = relationship("Dispute", back_populates="merchant", cascade="all, delete-orphan")

    # --- Timestamps ---
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    def __repr__(self) -> str:
        return (
            f"<Merchant(id={self.id}, paypal_id='{self.paypal_merchant_id}', "
            f"health={self.account_health_score}, risk='{self.risk_level}')>"
        )
