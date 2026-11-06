"""
DisputeShield AI — APIMatic OpenAPI Generator & SDK Exporter (Day 21)

Extracts the comprehensive OpenAPI 3.0 specification from the running FastAPI application,
enriches it with APIMatic code-generation metadata and language settings, and saves it to
`apimatic/disputeshield_openapi.json`.
"""

import json
import sys
from pathlib import Path

# Ensure backend root is on sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from main import app


def generate_openapi_spec():
    openapi_schema = app.openapi()

    # APIMatic codegen metadata enhancements
    openapi_schema["info"]["title"] = "DisputeShield AI API"
    openapi_schema["info"]["version"] = "1.0.0"
    openapi_schema["info"]["description"] = (
        "DisputeShield AI: Autonomous dispute defense agent for PayPal merchants. "
        "Provides REST endpoints for dispute triage, evidence generation, risk analytics, "
        "and webhook ingestion. Standardized OpenAPI 3.0 specification formatted for APIMatic SDK generation."
    )

    openapi_schema["servers"] = [
        {"url": "http://localhost:8000", "description": "Local development server"},
        {"url": "https://disputeshield.onrender.com", "description": "Production Render deployment"},
    ]

    # APIMatic specific extensions
    openapi_schema["x-codegen-settings"] = {
        "generateInterfaces": True,
        "languageSettings": {
            "typescript": {
                "packageName": "@disputeshield/sdk",
                "clientName": "DisputeShieldClient",
                "modelPackage": "models",
                "apiPackage": "api",
            },
            "python": {
                "packageName": "disputeshield_sdk",
                "clientName": "DisputeShieldClient",
            },
        },
    }

    out_dir = Path(__file__).resolve().parent.parent / "apimatic"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "disputeshield_openapi.json"

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(openapi_schema, f, indent=2)

    print(f"Successfully generated APIMatic OpenAPI schema at: {out_file}")
    return openapi_schema


if __name__ == "__main__":
    generate_openapi_spec()
