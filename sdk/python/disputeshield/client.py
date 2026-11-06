"""
DisputeShield AI — Official Python SDK Client
Generated & formatted for APIMatic and merchant automation pipelines.
"""

from typing import Any, Dict, List, Optional
import httpx


class DisputeShieldClient:
    """
    Client for interacting with the DisputeShield AI PayPal Dispute Defense API.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        api_key: Optional[str] = None,
        timeout: float = 15.0,
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def _request(self, method: str, path: str, **kwargs) -> Any:
        url = f"{self.base_url}{path if path.startswith('/') else '/' + path}"
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.request(method, url, headers=self.headers, **kwargs)
            resp.raise_for_status()
            return resp.json()

    # --- Disputes API ---

    def get_disputes(
        self,
        start_row: int = 0,
        end_row: int = 20,
        sort_col: Optional[str] = None,
        sort_dir: str = "asc",
        filter_tab: Optional[str] = None,
        search: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Fetch paginated dispute records for dashboard grids."""
        params: Dict[str, Any] = {
            "start_row": start_row,
            "end_row": end_row,
            "sort_dir": sort_dir,
        }
        if sort_col:
            params["sort_col"] = sort_col
        if filter_tab:
            params["filter_tab"] = filter_tab
        if search:
            params["search"] = search

        return self._request("GET", "/api/disputes", params=params)

    def get_dispute(self, dispute_id: str) -> Dict[str, Any]:
        """Fetch full details and evidence chain for a specific dispute."""
        return self._request("GET", f"/api/disputes/{dispute_id}")

    def submit_evidence(self, dispute_id: str, note: Optional[str] = None) -> Dict[str, Any]:
        """Approve and submit drafted evidence package to PayPal Resolution API."""
        return self._request("POST", f"/api/disputes/{dispute_id}/submit-evidence", json={"note": note})

    def override_decision(self, dispute_id: str, action: str, note: Optional[str] = None) -> Dict[str, Any]:
        """Override AI agent decision with manual merchant action."""
        return self._request("POST", f"/api/disputes/{dispute_id}/override", json={"action": action, "note": note})

    # --- Webhooks & Simulation ---

    def simulate_webhook(
        self,
        reason: Optional[str] = None,
        amount: Optional[str] = None,
        scenario_index: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Trigger a simulated PayPal webhook event across rotating dispute scenarios."""
        payload: Dict[str, Any] = {}
        if reason:
            payload["reason"] = reason
        if amount:
            payload["amount"] = amount
        if scenario_index is not None:
            payload["scenario_index"] = scenario_index

        return self._request("POST", "/api/webhooks/paypal/simulate", json=payload)

    # --- Analytics & Risk Engine ---

    def get_risk_score(self) -> Dict[str, Any]:
        """Fetch 90-day rolling dispute velocity and PayPal 1.5% limit telemetry."""
        return self._request("GET", "/api/analytics/risk-score")

    def get_summary(self) -> Dict[str, Any]:
        """Fetch high-level aggregate KPI metrics and resolution counters."""
        return self._request("GET", "/api/analytics/summary")

    def get_win_rate(self) -> Dict[str, Any]:
        """Fetch empirical win rate percentage and resolved dispute counts."""
        return self._request("GET", "/api/analytics/win-rate")

