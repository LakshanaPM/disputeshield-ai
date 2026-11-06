"""
DisputeShield AI — Webhook Pydantic Schemas

Schemas for PayPal webhook payloads.
"""

from pydantic import BaseModel
from typing import Optional, Any


class WebhookPayload(BaseModel):
    """
    Represents a PayPal webhook notification payload.
    Flexible schema since PayPal sends various event types.
    """
    id: str  # Event ID (for idempotency)
    event_type: str  # e.g., CUSTOMER.DISPUTE.CREATED
    resource_type: Optional[str] = None
    resource: Optional[Any] = None  # The dispute/order/etc. resource
    create_time: Optional[str] = None
    summary: Optional[str] = None
    event_version: Optional[str] = None
    resource_version: Optional[str] = None
