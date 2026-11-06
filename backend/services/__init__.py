"""DisputeShield AI — Services Package"""

try:
    from services.paypal_client import (
        PayPalClient,
        PayPalAPIError,
        PayPalAuthError,
        PayPalNotFoundError,
        PayPalValidationError,
    )
    from services.webhook_verifier import verify_paypal_webhook
    from services.evidence_chain import build_evidence_chain
    from services.elasticsearch_service import ElasticsearchService
    from services.mcp_bridge import MCPBridge, get_mcp_tools
    from services.risk_predictor import RiskPredictor, RiskAssessment
except (ImportError, ModuleNotFoundError):
    from .paypal_client import (
        PayPalClient,
        PayPalAPIError,
        PayPalAuthError,
        PayPalNotFoundError,
        PayPalValidationError,
    )
    from .webhook_verifier import verify_paypal_webhook
    from .evidence_chain import build_evidence_chain
    from .elasticsearch_service import ElasticsearchService
    from .mcp_bridge import MCPBridge, get_mcp_tools
    from .risk_predictor import RiskPredictor, RiskAssessment

__all__ = [
    "PayPalClient",
    "PayPalAPIError",
    "PayPalAuthError",
    "PayPalNotFoundError",
    "PayPalValidationError",
    "verify_paypal_webhook",
    "build_evidence_chain",
    "ElasticsearchService",
    "MCPBridge",
    "get_mcp_tools",
    "RiskPredictor",
    "RiskAssessment",
]


