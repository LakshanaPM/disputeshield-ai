"""
DisputeShield AI — PayPal REST API Client

Async HTTP client using httpx.AsyncClient for communicating with the PayPal
Developer Sandbox and Production APIs. Handles OAuth2 Client Credentials
token management with pre-expiry caching buffer, structured error responses,
and customer dispute endpoints.
"""

import asyncio
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
import httpx

# Ensure backend root is on sys.path for direct script execution
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from config import settings

logger = logging.getLogger(__name__)


# ============================================================
# Structured Exceptions
# ============================================================

class PayPalAPIError(Exception):
    """Base exception for PayPal API communication errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        error_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.error_data = error_data or {}


class PayPalAuthError(PayPalAPIError):
    """Raised on 401 Unauthorized or OAuth2 token failure."""
    pass


class PayPalNotFoundError(PayPalAPIError):
    """Raised on 404 Resource Not Found errors."""
    pass


class PayPalValidationError(PayPalAPIError):
    """Raised on 422 Unprocessable Entity / validation failures."""
    pass


# ============================================================
# PayPal Async Client
# ============================================================

class PayPalClient:
    """
    Async client for PayPal REST APIs.

    Features:
    - OAuth2 Client Credentials grant with automatic token caching.
    - Pre-expiry refresh buffer (default 120 seconds).
    - Structured error parsing for 401, 404, 422, and 5xx responses.
    - Dispute management: list_disputes, get_dispute_details.
    """

    TOKEN_BUFFER_SECONDS = 120  # Refresh 2 minutes before actual expiry

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.client_id = client_id or settings.paypal_client_id
        self.client_secret = client_secret or settings.paypal_client_secret
        self.base_url = (base_url or settings.paypal_base_url).rstrip("/")
        self.timeout = timeout

        self._http_client: Optional[httpx.AsyncClient] = None
        self._access_token: Optional[str] = None
        self._token_expires_at: Optional[float] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the underlying persistent httpx.AsyncClient."""
        if self._http_client is None or self._http_client.is_closed:
            self._http_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._http_client

    async def close(self) -> None:
        """Close the underlying HTTP client session."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None

    async def __aenter__(self) -> "PayPalClient":
        await self._get_client()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    # --- Authentication ---

    async def get_access_token(self, force_refresh: bool = False) -> str:
        """
        Retrieve a valid OAuth2 access token, renewing it if expired or nearing expiry.
        Uses HTTP Basic Auth against /v1/oauth2/token with grant_type=client_credentials.
        """
        now = time.time()
        if (
            not force_refresh
            and self._access_token
            and self._token_expires_at
            and (now + self.TOKEN_BUFFER_SECONDS < self._token_expires_at)
        ):
            return self._access_token

        if not self.client_id or not self.client_secret:
            raise PayPalAuthError(
                "PayPal client_id and client_secret must be set in environment or config.",
                status_code=401,
            )

        client = await self._get_client()
        logger.debug("Requesting fresh PayPal OAuth2 access token...")

        try:
            response = await client.post(
                "/v1/oauth2/token",
                data={"grant_type": "client_credentials"},
                auth=(self.client_id, self.client_secret),
                headers={
                    "Accept": "application/json",
                    "Accept-Language": "en_US",
                },
            )
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error while authenticating with PayPal: {exc}") from exc

        if response.status_code == 401:
            raise PayPalAuthError(
                "Failed to authenticate with PayPal: Invalid client credentials (401).",
                status_code=401,
                error_data=response.json() if response.content else {},
            )

        if response.is_error:
            raise PayPalAPIError(
                f"PayPal OAuth2 token endpoint returned error {response.status_code}: {response.text}",
                status_code=response.status_code,
                error_data=response.json() if response.content else {},
            )

        token_data = response.json()
        self._access_token = token_data.get("access_token")
        expires_in = token_data.get("expires_in", 3600)
        self._token_expires_at = now + float(expires_in)

        logger.info(f"Obtained PayPal OAuth2 token (valid for {expires_in}s).")
        return self._access_token

    # --- Core Request Handler ---

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        retry_on_auth_fail: bool = True,
    ) -> Dict[str, Any]:
        """
        Execute an authenticated request against the PayPal REST API with structured error handling.
        """
        token = await self.get_access_token()
        req_headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if headers:
            req_headers.update(headers)

        client = await self._get_client()
        url = endpoint if endpoint.startswith("/") else f"/{endpoint}"

        try:
            response = await client.request(
                method=method,
                url=url,
                params=params,
                json=json_data,
                headers=req_headers,
            )
        except httpx.RequestError as exc:
            raise PayPalAPIError(f"Network error during PayPal API request to {url}: {exc}") from exc

        # Handle 401 Token Expiration / Invalidation
        if response.status_code == 401 and retry_on_auth_fail:
            logger.warning("PayPal returned 401 Unauthorized; refreshing access token and retrying...")
            self._access_token = None
            self._token_expires_at = None
            return await self._request(
                method, endpoint, params, json_data, headers, retry_on_auth_fail=False
            )

        # Parse response body
        try:
            data = response.json() if response.content else {}
        except Exception:
            data = {"raw_response": response.text}

        # Structured error mapping
        if response.status_code == 401:
            raise PayPalAuthError(
                f"PayPal Unauthorized (401): {data.get('message', 'Authentication failed')}",
                status_code=401,
                error_data=data,
            )
        elif response.status_code == 404:
            raise PayPalNotFoundError(
                f"PayPal Resource Not Found (404): {data.get('message', f'Endpoint {url} not found')}",
                status_code=404,
                error_data=data,
            )
        elif response.status_code == 422:
            details = data.get("details", [])
            detail_msg = "; ".join(d.get("description", "") for d in details if "description" in d)
            raise PayPalValidationError(
                f"PayPal Validation Error (422): {data.get('message', '')} {detail_msg}".strip(),
                status_code=422,
                error_data=data,
            )
        elif response.is_error:
            raise PayPalAPIError(
                f"PayPal API error ({response.status_code}): {data.get('message', response.text)}",
                status_code=response.status_code,
                error_data=data,
            )

        return data

    # --- Disputes Endpoints (Day 2) ---

    async def list_disputes(
        self,
        status: Optional[str] = None,
        start_time: Optional[str] = None,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        List disputes for the authenticated merchant account.
        Calls GET /v1/customer/disputes.
        """
        params: Dict[str, Any] = {"page_size": min(page_size, 50)}
        if status:
            params["dispute_state"] = status
        if start_time:
            params["start_time"] = start_time

        return await self._request("GET", "/v1/customer/disputes", params=params)

    async def get_dispute_details(self, dispute_id: str) -> Dict[str, Any]:
        """
        Retrieve full details for a specific dispute by its PayPal dispute ID.
        Calls GET /v1/customer/disputes/{dispute_id}.
        """
        if not dispute_id:
            raise ValueError("dispute_id is required")
        return await self._request("GET", f"/v1/customer/disputes/{dispute_id}")

    # --- Dispute Action Endpoints (Day 4) ---

    async def provide_evidence(
        self,
        dispute_id: str,
        evidence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Submit defense evidence to PayPal for an active dispute.
        Calls POST /v1/customer/disputes/{dispute_id}/provide-evidence.
        """
        if not dispute_id:
            raise ValueError("dispute_id is required")
        return await self._request(
            "POST",
            f"/v1/customer/disputes/{dispute_id}/provide-evidence",
            json_data=evidence,
        )

    async def accept_claim(
        self,
        dispute_id: str,
        note: Optional[str] = None,
        accept_claim_type: str = "REFUND",
    ) -> Dict[str, Any]:
        """
        Accept a dispute claim and issue a refund/resolution.
        Calls POST /v1/customer/disputes/{dispute_id}/accept-claim.
        """
        if not dispute_id:
            raise ValueError("dispute_id is required")
        payload: Dict[str, Any] = {"accept_claim_type": accept_claim_type}
        if note:
            payload["note"] = note
        return await self._request(
            "POST",
            f"/v1/customer/disputes/{dispute_id}/accept-claim",
            json_data=payload,
        )

    async def appeal_dispute(
        self,
        dispute_id: str,
        evidence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Appeal a lost dispute by submitting additional supporting evidence.
        Calls POST /v1/customer/disputes/{dispute_id}/appeal.
        """
        if not dispute_id:
            raise ValueError("dispute_id is required")
        return await self._request(
            "POST",
            f"/v1/customer/disputes/{dispute_id}/appeal",
            json_data=evidence,
        )

    # --- Orders & Shipment Tracking Endpoints (Day 5) ---

    async def get_order(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch order details from the PayPal Orders v2 API.
        Calls GET /v2/checkout/orders/{order_id}.
        Returns None if order is not found (404).
        """
        if not order_id:
            raise ValueError("order_id is required")
        try:
            return await self._request("GET", f"/v2/checkout/orders/{order_id}")
        except PayPalNotFoundError:
            logger.warning(f"PayPal order '{order_id}' not found (404).")
            return None

    async def get_tracking(self, tracker_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch shipment tracking details for a specific tracker ID.
        Calls GET /v1/shipping/trackers/{tracker_id}.
        Returns None if tracker is not found (404).
        """
        if not tracker_id:
            raise ValueError("tracker_id is required")
        try:
            return await self._request("GET", f"/v1/shipping/trackers/{tracker_id}")
        except PayPalNotFoundError:
            logger.warning(f"PayPal shipment tracker '{tracker_id}' not found (404).")
            return None

    async def list_trackers(
        self,
        transaction_id: Optional[str] = None,
        tracking_number: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        List shipment trackers filtered by transaction_id or tracking_number.
        Calls GET /v1/shipping/trackers.
        """
        params: Dict[str, Any] = {}
        if transaction_id:
            params["transaction_id"] = transaction_id
        if tracking_number:
            params["tracking_number"] = tracking_number
        try:
            return await self._request("GET", "/v1/shipping/trackers", params=params)
        except PayPalNotFoundError:
            return {"trackers": []}

    # --- Invoicing API Endpoints (Day 6) ---

    async def get_invoice(self, invoice_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetch invoice details from the PayPal Invoicing v2 API.
        Calls GET /v2/invoicing/invoices/{invoice_id}.
        Returns None if invoice is not found (404).
        """
        if not invoice_id:
            raise ValueError("invoice_id is required")
        try:
            return await self._request("GET", f"/v2/invoicing/invoices/{invoice_id}")
        except PayPalNotFoundError:
            logger.warning(f"PayPal invoice '{invoice_id}' not found (404).")
            return None

    async def list_invoices(
        self,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict[str, Any]:
        """
        List invoices from the PayPal Invoicing v2 API.
        Calls GET /v2/invoicing/invoices.
        """
        params = {
            "page": max(page, 1),
            "page_size": min(max(page_size, 1), 100),
            "total_required": "true",
        }
        try:
            return await self._request("GET", "/v2/invoicing/invoices", params=params)
        except PayPalNotFoundError:
            return {"invoices": [], "total_items": 0}


# ============================================================
# Sandbox Verification Test Block
# ============================================================

if __name__ == "__main__":
    async def main():
        print("=" * 60)
        print("DisputeShield AI — PayPal Sandbox Client Verification")
        print("=" * 60)
        print(f"Base URL:      {settings.paypal_base_url}")
        print(f"Environment:   {settings.paypal_environment}")
        print(f"Client ID:     {'[CONFIGURED]' if settings.paypal_client_id else '[NOT CONFIGURED]'}")
        print("-" * 60)

        async with PayPalClient() as client:
            try:
                print("1. Testing OAuth2 Token generation...")
                token = await client.get_access_token()
                print(f"   [SUCCESS] Received OAuth2 Token: {token[:12]}...{token[-6:]}")

                print("\n2. Testing GET /v1/customer/disputes...")
                disputes = await client.list_disputes(page_size=5)
                items = disputes.get("items", [])
                print(f"   [SUCCESS] Connected to PayPal Disputes API.")
                print(f"   Disputes found in sandbox: {len(items)}")
                for item in items:
                    print(f"   - ID: {item.get('dispute_id')}, Reason: {item.get('reason')}, Status: {item.get('status')}")

            except PayPalAuthError as auth_err:
                print(f"   [AUTH RESULT] {auth_err}")
                print("   Note: Expected when credentials are not yet populated in .env.")
            except PayPalAPIError as api_err:
                print(f"   [API RESULT ({api_err.status_code})] {api_err}")
                if api_err.error_data:
                    print(f"   Details: {api_err.error_data}")
            except Exception as exc:
                print(f"   [UNEXPECTED ERROR] {exc}")

        print("=" * 60)

    asyncio.run(main())
