"""
DisputeShield AI — PayPal Webhook Signature Verifier

Verifies incoming PayPal webhook notifications against PayPal's verification API:
POST /v1/notifications/verify-webhook-signature
"""

import json
import logging
from typing import Any, Dict, Optional, Union

from config import settings
from services.paypal_client import PayPalClient, PayPalAPIError

logger = logging.getLogger(__name__)


async def verify_paypal_webhook(
    headers: Dict[str, str],
    event_body: Union[str, bytes, Dict[str, Any]],
    webhook_id: Optional[str] = None,
    client: Optional[PayPalClient] = None,
) -> bool:
    """
    Verify PayPal webhook signature using PayPal's REST verification endpoint.

    Required transmission headers:
    - PAYPAL-TRANSMISSION-ID
    - PAYPAL-TRANSMISSION-TIME
    - PAYPAL-CERT-URL
    - PAYPAL-AUTH-ALGO
    - PAYPAL-TRANSMISSION-SIG
    """
    effective_webhook_id = webhook_id or settings.paypal_webhook_id
    is_dev = getattr(settings, "environment", "development").lower() == "development" or settings.app_debug
    is_placeholder_webhook = not effective_webhook_id or effective_webhook_id.startswith("your_")

    # Debug bypass for local development before an active webhook ID is registered
    if is_dev and is_placeholder_webhook:
        logger.warning(
            "Bypassing PayPal webhook signature verification (development mode & unconfigured PAYPAL_WEBHOOK_ID)."
        )
        return True

    # Case-insensitive header extraction
    normalized = {k.lower(): v for k, v in headers.items()}
    transmission_id = normalized.get("paypal-transmission-id")
    transmission_time = normalized.get("paypal-transmission-time")
    cert_url = normalized.get("paypal-cert-url")
    auth_algo = normalized.get("paypal-auth-algo")
    transmission_sig = normalized.get("paypal-transmission-sig")

    if not all([transmission_id, transmission_time, cert_url, auth_algo, transmission_sig]):
        logger.warning(
            "Missing one or more required PayPal transmission headers for signature verification."
        )
        return False

    if isinstance(event_body, (str, bytes)):
        try:
            webhook_event = json.loads(event_body)
        except Exception as exc:
            logger.error(f"Failed to parse webhook JSON payload for signature verification: {exc}")
            return False
    else:
        webhook_event = event_body

    verification_payload = {
        "transmission_id": transmission_id,
        "transmission_time": transmission_time,
        "cert_url": cert_url,
        "auth_algo": auth_algo,
        "transmission_sig": transmission_sig,
        "webhook_id": effective_webhook_id,
        "webhook_event": webhook_event,
    }

    owns_client = False
    if client is None:
        client = PayPalClient()
        owns_client = True

    try:
        logger.debug(f"Verifying webhook event with transmission_id: {transmission_id}")
        result = await client._request(
            method="POST",
            endpoint="/v1/notifications/verify-webhook-signature",
            json_data=verification_payload,
        )
        status = result.get("verification_status", "").upper()
        logger.info(f"PayPal webhook verification result: {status}")
        return status == "SUCCESS"
    except PayPalAPIError as exc:
        logger.error(f"PayPal webhook verification API call failed: {exc}")
        return False
    except Exception as exc:
        logger.error(f"Unexpected error during webhook verification: {exc}")
        return False
    finally:
        if owns_client:
            await client.close()
