#!/usr/bin/env bash
# DisputeShield AI — PayPal MCP Server Startup Script
# Boots @paypal/mcp stdio protocol server with Sandbox credentials.

set -e

# 1. Environment & Credentials Configuration
export PAYPAL_ENVIRONMENT="${PAYPAL_ENVIRONMENT:-SANDBOX}"

if [ -z "$PAYPAL_ACCESS_TOKEN" ]; then
    if [ -n "$PAYPAL_CLIENT_ID" ] && [ -n "$PAYPAL_CLIENT_SECRET" ]; then
        echo "[MCP Startup] Acquiring fresh OAuth2 token for PayPal Sandbox..." >&2
        PAYPAL_ACCESS_TOKEN=$(curl -s -X POST "https://api-m.sandbox.paypal.com/v1/oauth2/token" \
            -u "${PAYPAL_CLIENT_ID}:${PAYPAL_CLIENT_SECRET}" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "grant_type=client_credentials" | grep -o '"access_token": *"[^"]*"' | awk -F'"' '{print $4}')
        export PAYPAL_ACCESS_TOKEN
        echo "[MCP Startup] Successfully acquired fresh access token." >&2
    else
        echo "[MCP Startup] Notice: PAYPAL_CLIENT_ID/SECRET not set in environment. Using dev placeholder token." >&2
        export PAYPAL_ACCESS_TOKEN="SANDBOX_DEV_FALLBACK_TOKEN"
    fi
fi

# 2. Launch PayPal MCP Server via stdio
echo "[MCP Startup] Launching @paypal/mcp server with --tools=all..." >&2
exec npx -y @paypal/mcp --tools=all
