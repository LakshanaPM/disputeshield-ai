"""
DisputeShield AI — Elasticsearch & Invoicing Integration Tests (Day 6)

Validates:
1. Cosine similarity calculation helper.
2. ElasticsearchService index creation with dense_vector mappings.
3. Document indexing and full-text keyword search across buyer messages and reasons.
4. kNN dense vector similarity search (1536-dim embedding vectors, cosine ranking).
5. PayPalClient Invoicing v2 methods: get_invoice, list_invoices, and 404 handling.
"""

import asyncio
import math
import os
import sys
from unittest.mock import AsyncMock, patch

os.environ["DATABASE_URL"] = "sqlite:///./test_es.db"
sys.path.insert(0, "backend")

from services.elasticsearch_service import ElasticsearchService, _cosine_similarity
from services.paypal_client import PayPalClient, PayPalNotFoundError



def approx_equal(a: float, b: float, tol: float = 1e-3) -> bool:
    return abs(a - b) <= tol


def test_cosine_similarity():
    # Identical
    v = [1.0, 0.0, 0.0]
    assert approx_equal(_cosine_similarity(v, v), 1.0)

    # Orthogonal
    v1 = [1.0, 0.0, 0.0]
    v2 = [0.0, 1.0, 0.0]
    assert approx_equal(_cosine_similarity(v1, v2), 0.0)

    # Mismatched/empty
    assert _cosine_similarity([], [1.0]) == 0.0
    assert _cosine_similarity([1.0], [1.0, 2.0]) == 0.0
    assert _cosine_similarity([0.0, 0.0], [0.0, 0.0]) == 0.0
    print("[TEST 1 PASSED: Cosine similarity helper correctly computes vector angles]")


async def test_ensure_index():
    service = ElasticsearchService()
    try:
        success = await service.ensure_index("test_disputes")
        assert success is True
        print("[TEST 2 PASSED: ElasticsearchService ensure_index succeeded]")
    finally:
        await service.close()


async def test_index_and_fulltext_search():
    service = ElasticsearchService()
    try:
        # Populate test dispute documents
        doc1 = {
            "dispute_id": "PP-D-1001",
            "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
            "status": "UNDER_REVIEW",
            "amount": 249.99,
            "buyer_message": "I never received the wireless noise-canceling headphones I ordered.",
            "evidence_summary": "Carrier tracking shows delivered to front porch.",
        }
        doc2 = {
            "dispute_id": "PP-D-1002",
            "reason": "UNAUTHORISED",
            "status": "RESOLVED",
            "amount": 49.00,
            "buyer_message": "Unfamiliar recurring software subscription charge on statement.",
            "evidence_summary": "User logged in with 2FA from verified IP address.",
        }

        await service.index_dispute(doc1)
        await service.index_dispute(doc2)

        # 1. Search for "headphones"
        results = await service.search_disputes("headphones")
        assert len(results) == 1
        assert results[0]["dispute_id"] == "PP-D-1001"

        # 2. Search for "subscription"
        sub_results = await service.search_disputes("subscription")
        assert len(sub_results) == 1
        assert sub_results[0]["dispute_id"] == "PP-D-1002"

        # 3. Search with matching reason filter
        filtered = await service.search_disputes("ordered", reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED")
        assert len(filtered) == 1
        assert filtered[0]["dispute_id"] == "PP-D-1001"

        # 4. Search with non-matching reason filter
        filtered_mismatch = await service.search_disputes("ordered", reason="UNAUTHORISED")
        assert len(filtered_mismatch) == 0

        print("[TEST 3 PASSED: Full-text multi-match search and reason filtering succeeded]")

    finally:
        await service.close()


async def test_knn_vector_search():
    service = ElasticsearchService()
    try:
        dim = ElasticsearchService.VECTOR_DIM

        # Vector A: heavy in first dimension
        vec_a = [0.0] * dim
        vec_a[0] = 1.0

        # Vector B: similar to A (slight angle)
        vec_b = [0.0] * dim
        vec_b[0] = 0.95
        vec_b[1] = 0.31

        # Vector C: orthogonal in dimension 50
        vec_c = [0.0] * dim
        vec_c[50] = 1.0

        await service.index_dispute(
            {"dispute_id": "PP-D-2001", "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED", "buyer_message": "Item missing"},
            vector=vec_a,
        )
        await service.index_dispute(
            {"dispute_id": "PP-D-2002", "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED", "buyer_message": "Package lost"},
            vector=vec_b,
        )
        await service.index_dispute(
            {"dispute_id": "PP-D-2003", "reason": "UNAUTHORISED", "buyer_message": "Card compromised"},
            vector=vec_c,
        )

        # Query using a vector identical to vec_a
        query_vec = [0.0] * dim
        query_vec[0] = 1.0

        hits = await service.vector_search(query_vec, k=2)
        assert len(hits) == 2
        # Highest match should be PP-D-2001 (cosine = 1.0)
        assert hits[0]["dispute_id"] == "PP-D-2001"
        assert approx_equal(hits[0]["_score"], 1.0)

        # Second highest match should be PP-D-2002
        assert hits[1]["dispute_id"] == "PP-D-2002"
        assert hits[1]["_score"] > 0.9

        print("[TEST 4 PASSED: kNN dense vector cosine similarity search ranked documents correctly]")

    finally:
        await service.close()


async def test_paypal_invoicing():
    client = PayPalClient(client_id="dummy_id", client_secret="dummy_sec")
    try:
        mock_invoice = {
            "id": "INV2-TEST-1234",
            "status": "PAID",
            "detail": {"invoice_number": "0001", "currency_code": "USD"},
        }

        # 1. Test get_invoice success
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_invoice
            result = await client.get_invoice("INV2-TEST-1234")
            mock_req.assert_awaited_once_with("GET", "/v2/invoicing/invoices/INV2-TEST-1234")
            assert result == mock_invoice
            assert result["status"] == "PAID"

        # 2. Test get_invoice 404 handling
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.side_effect = PayPalNotFoundError("Invoice not found", status_code=404)
            result = await client.get_invoice("INV2-NONEXISTENT")
            assert result is None

        # 3. Test list_invoices
        mock_list = {
            "total_items": 1,
            "items": [{"id": "INV2-001", "status": "SENT"}],
        }
        with patch.object(client, "_request", new_callable=AsyncMock) as mock_req:
            mock_req.return_value = mock_list
            res_list = await client.list_invoices(page=1, page_size=10)
            mock_req.assert_awaited_once_with(
                "GET",
                "/v2/invoicing/invoices",
                params={"page": 1, "page_size": 10, "total_required": "true"},
            )
            assert res_list["total_items"] == 1
            assert len(res_list["items"]) == 1

        print("[TEST 5 PASSED: PayPalClient Invoicing v2 get_invoice, list_invoices, and 404 trapping]")

    finally:
        await client.close()


def run_all_tests():
    print("=" * 60)
    print("DisputeShield AI — Running Day 6 Integration Tests")
    print("=" * 60)
    test_cosine_similarity()

    async def _async_suite():
        await test_ensure_index()
        await test_index_and_fulltext_search()
        await test_knn_vector_search()
        await test_paypal_invoicing()

    asyncio.run(_async_suite())
    print("=" * 60)
    print("ALL DAY 6 TESTS PASSED SUCCESSFULLY (5/5)")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
