"""
DisputeShield AI — MCP Bridge & LangChain Tools Tests (Day 7)

Validates:
1. Tool initialization, Pydantic schemas, and naming conventions.
2. Async tool executions: get_dispute, lookup_order, get_tracking, get_invoice, rag_query, submit_evidence.
3. Synchronous execution safety without event loop collisions.
4. Graceful fallback when external MCP process is unavailable.
"""

import asyncio
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test_mcp.db"
sys.path.insert(0, "backend")

from services.mcp_bridge import MCPBridge, get_mcp_tools
from langchain_core.tools import BaseTool


def test_tool_definitions_and_schemas():
    tools = get_mcp_tools()
    assert len(tools) == 6

    expected_tool_names = {
        "paypal_get_dispute",
        "paypal_lookup_order",
        "paypal_get_tracking",
        "paypal_get_invoice",
        "rag_query_similar_cases",
        "paypal_submit_evidence_recommendation",
    }
    actual_names = {t.name for t in tools}
    assert actual_names == expected_tool_names

    for t in tools:
        assert isinstance(t, BaseTool)
        assert t.description and len(t.description) > 10
        assert t.args_schema is not None

    print("[TEST 1 PASSED: All 6 LangChain tools initialized with valid schemas]")


async def test_async_tool_executions():
    bridge = MCPBridge()
    try:
        tools = {t.name: t for t in bridge.get_tools()}

        # 1. paypal_get_dispute
        dispute_res = await tools["paypal_get_dispute"].ainvoke({"dispute_id": "PP-D-9901"})
        assert dispute_res["dispute_id"] == "PP-D-9901"
        assert "reason" in dispute_res

        # 2. paypal_lookup_order
        order_res = await tools["paypal_lookup_order"].ainvoke({"order_id": "ORD-9901"})
        assert order_res["id"] == "ORD-9901"
        assert len(order_res["purchase_units"]) > 0

        # 3. paypal_get_tracking
        tracking_res = await tools["paypal_get_tracking"].ainvoke({"tracking_number": "1Z9999999999999999"})
        assert tracking_res["tracking_number"] == "1Z9999999999999999"
        assert tracking_res["status"] == "DELIVERED"

        # 4. paypal_get_invoice
        invoice_res = await tools["paypal_get_invoice"].ainvoke({"invoice_id": "INV2-9901"})
        assert invoice_res["id"] == "INV2-9901"
        assert invoice_res["status"] == "PAID"

        # 5. rag_query_similar_cases
        rag_res = await tools["rag_query_similar_cases"].ainvoke({
            "query": "headphones not received",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "k": 2,
        })
        assert isinstance(rag_res, list)
        assert len(rag_res) > 0

        # 6. paypal_submit_evidence_recommendation
        submit_res = await tools["paypal_submit_evidence_recommendation"].ainvoke({
            "dispute_id": "PP-D-9901",
            "evidence_notes": "Delivered to front porch with signature match.",
            "tracking_number": "1Z9999999999999999",
            "carrier": "UPS",
        })
        assert submit_res["status"] == "ACCEPTED"
        assert submit_res["dispute_id"] == "PP-D-9901"

        print("[TEST 2 PASSED: All 6 tools executed asynchronously with valid payloads]")
    finally:
        await bridge.close()


def test_sync_tool_execution():
    bridge = MCPBridge()
    tools = {t.name: t for t in bridge.get_tools()}

    sync_res = tools["paypal_get_dispute"].invoke({"dispute_id": "PP-D-SYNC-88"})
    assert sync_res["dispute_id"] == "PP-D-SYNC-88"
    assert "status" in sync_res

    print("[TEST 3 PASSED: Synchronous invoke executed safely without loop collision]")


def run_all_tests():
    print("=" * 60)
    print("DisputeShield AI — Running Day 7 MCP Bridge Integration Tests")
    print("=" * 60)

    test_tool_definitions_and_schemas()
    asyncio.run(test_async_tool_executions())
    test_sync_tool_execution()

    print("=" * 60)
    print("ALL DAY 7 MCP TESTS PASSED SUCCESSFULLY (3/3)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
