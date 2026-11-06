"""
DisputeShield AI — Webhook Event ORM Model

Raw audit log of every webhook event received from PayPal.
Used for idempotency checks and debugging.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func

from database import Base


class WebhookEvent(Base):
    """
    Raw webhook event log. Every event from PayPal is stored
    here before processing for audit trail and idempotency.
    """
    __tablename__ = "webhook_events"

    id = Column(Integer, primary_key=True, autoincrement=True)

    # --- PayPal Event Identifiers ---
    event_id = Column(String(100), unique=True, nullable=False, index=True)
    event_type = Column(String(100), nullable=False, index=True)
    resource_type = Column(String(100), nullable=True)
    resource_id = Column(String(100), nullable=True)

    # --- Raw Payload ---
    payload = Column(Text, nullable=False)  # Full JSON payload

    # --- Processing Status ---
    processed = Column(Boolean, nullable=False, default=False)
    processing_error = Column(Text, nullable=True)

    # --- Timestamps ---
    paypal_create_time = Column(DateTime, nullable=True)
    received_at = Column(DateTime, server_default=func.now(), nullable=False)
    processed_at = Column(DateTime, nullable=True)

    def __repr__(self) -> str:
        return (
            f"<WebhookEvent(id={self.id}, event_id='{self.event_id}', "
            f"type='{self.event_type}', processed={self.processed})>"
        )
