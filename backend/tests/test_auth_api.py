"""
Unit tests for DisputeShield AI Authentication API endpoints.
"""

import sys
import os
from pathlib import Path

backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_login_demo_merchant():
    """Test standard email/password login with demo merchant credentials."""
    response = client.post(
        "/api/auth/login",
        json={"email": "merchant@elitemerchant.com", "password": "password123"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "merchant@elitemerchant.com"
    assert data["business_name"] == "EliteMerchant LLC"
    assert data["verified"] is True
    assert "token" in data


def test_login_paypal_sandbox_1click():
    """Test 1-click PayPal sandbox authentication."""
    response = client.post("/api/auth/paypal")
    assert response.status_code == 200
    data = response.json()
    assert data["paypal_merchant_id"] == "MERCHANT-84920"
    assert data["business_name"] == "EliteMerchant LLC"


def test_login_empty_password_rejected():
    """Test that empty password fails for demo merchant."""
    response = client.post(
        "/api/auth/login",
        json={"email": "merchant@elitemerchant.com", "password": ""},
    )
    assert response.status_code == 400


def test_get_current_user_me():
    """Test /api/auth/me session query."""
    response = client.get("/api/auth/me")
    assert response.status_code == 200
    assert response.json()["business_name"] == "EliteMerchant LLC"


def test_logout():
    """Test /api/auth/logout endpoint."""
    response = client.post("/api/auth/logout")
    assert response.status_code == 200
    assert response.json()["success"] is True
