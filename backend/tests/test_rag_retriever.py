"""
DisputeShield AI — RAG Retriever Unit Tests (Day 12)

Validates:
1. Deterministic 1536-dim vector embedding generation, unit normalization, and determinism.
2. Empty text handling returning valid normalized unit vector.
3. Precedent retrieval with empirical win-rate computation and curated INR fallback.
4. Curated fallback for SNAD disputes with correct win-rate and strategy extraction.
5. In-memory mock store kNN vector retrieval calculating accurate empirical metrics.
"""

import asyncio
import math
import os
import sys
from pathlib import Path
from typing import Any, Dict, List

# Ensure backend directory is in sys.path
backend_dir = Path(__file__).resolve().parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Ensure test DB doesn't interfere
os.environ["DATABASE_URL"] = "sqlite:///./test_rag.db"

from agent.rag_retriever import RAGRetriever, _deterministic_embedding
from services.elasticsearch_service import ElasticsearchService


def test_deterministic_embedding_properties():
    """Verify vector properties: length, unit normalization, and determinism."""
    text = "Buyer claims item was not received at residential address."
    vec1 = _deterministic_embedding(text, dim=1536)
    vec2 = _deterministic_embedding(text, dim=1536)

    # 1. Dimension check
    assert len(vec1) == 1536
    assert len(vec2) == 1536

    # 2. Determinism check
    assert vec1 == vec2

    # 3. Normalization (L2 norm should be ~1.0)
    norm = math.sqrt(sum(x * x for x in vec1))
    assert abs(norm - 1.0) < 1e-5

    # 4. Variation check with different text
    diff_text = "Completely different reason merchandise not as described"
    vec3 = _deterministic_embedding(diff_text, dim=1536)
    assert vec1 != vec3
    print("[TEST 1 PASSED: Deterministic 1536-dim vector embedding and L2 normalization verified]")


def test_deterministic_embedding_empty_text():
    """Empty text should still return a valid normalized unit vector."""
    vec = _deterministic_embedding("", dim=1536)
    assert len(vec) == 1536
    assert vec[0] == 1.0
    norm = math.sqrt(sum(x * x for x in vec))
    assert abs(norm - 1.0) < 1e-5
    print("[TEST 2 PASSED: Empty text vector handling verified]")


def test_retrieve_curated_fallback_inr():
    """When ES has no matching records, fallback to curated INR precedents."""
    es_service = ElasticsearchService()
    es_service._mock_store.clear()  # Ensure empty

    async def _test():
        try:
            retriever = RAGRetriever(es_service=es_service)
            return await retriever.retrieve_similar_cases(
                dispute_text="Package was stolen or never arrived at my house",
                reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                k=3,
            )
        finally:
            if es_service.client:
                await es_service.client.close()

    result = asyncio.run(_test())

    assert "cases" in result
    assert len(result["cases"]) >= 2
    assert "win_rate" in result
    assert 0.0 <= result["win_rate"] <= 1.0
    assert "summary" in result
    assert "similar historical dispute precedents" in result["summary"]
    assert len(result["top_evidence_strategies"]) >= 1
    print(f"[TEST 3 PASSED: Curated fallback INR returned {len(result['cases'])} cases with {result['win_rate']*100:.1f}% win rate]")


def test_retrieve_curated_fallback_snad():
    """When ES is empty, returns curated SNAD precedents."""
    es_service = ElasticsearchService()
    es_service._mock_store.clear()

    async def _test():
        try:
            retriever = RAGRetriever(es_service=es_service)
            return await retriever.retrieve_similar_cases(
                dispute_text="Item color and size completely mismatch listing",
                reason="MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
                k=3,
            )
        finally:
            if es_service.client:
                await es_service.client.close()

    result = asyncio.run(_test())

    assert len(result["cases"]) == 3
    # In fallback SNAD, 2 won, 1 lost -> 2/3 = 0.67
    assert result["win_rate"] == 0.67
    assert any("specification sheet" in s.lower() for s in result["top_evidence_strategies"])
    print(f"[TEST 4 PASSED: Curated fallback SNAD returned 3 cases with {result['win_rate']*100:.1f}% win rate and top strategies]")


def test_vector_search_with_mock_es_store():
    """Verify kNN vector search finds the closest cases from indexed mock store."""
    es_service = ElasticsearchService()
    es_service._mock_store.clear()

    retriever = RAGRetriever(es_service=es_service)

    async def _setup_and_search():
        try:
            # Index 2 precedents
            case1_text = "Delivered package with UPS tracking signature confirmation"
            vec1 = await retriever.get_embedding(case1_text)
            await es_service.index_dispute({
                "dispute_id": "PRECEDENT-101",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": "RESOLVED",
                "outcome": "WON",
                "amount": 150.0,
                "evidence_summary": "UPS tracking showed signed delivery.",
            }, vector=vec1)

            case2_text = "Tracking shows lost in transit by carrier"
            vec2 = await retriever.get_embedding(case2_text)
            await es_service.index_dispute({
                "dispute_id": "PRECEDENT-102",
                "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                "status": "RESOLVED",
                "outcome": "LOST",
                "amount": 200.0,
                "evidence_summary": "Carrier lost shipment.",
            }, vector=vec2)

            # Query similar to case 1
            query_text = "UPS tracking proof of delivery signature required"
            return await retriever.retrieve_similar_cases(
                dispute_text=query_text,
                reason="MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
                k=2,
            )
        finally:
            if es_service.client:
                await es_service.client.close()

    result = asyncio.run(_setup_and_search())

    assert len(result["cases"]) == 2
    # Case 101 should be the top hit due to higher cosine similarity with UPS delivery
    assert result["cases"][0]["dispute_id"] == "PRECEDENT-101"
    assert result["win_rate"] == 0.5  # 1 won, 1 lost out of 2 hits
    assert "UPS tracking showed signed delivery." in result["top_evidence_strategies"]
    print(f"[TEST 5 PASSED: kNN mock vector search correctly retrieved top matches with empirical win rate {result['win_rate']*100:.1f}%]")


def run_all_tests():
    print("=" * 65)
    print("DisputeShield AI — Running Day 12 RAG Precedent Retriever Tests")
    print("=" * 65)
    test_deterministic_embedding_properties()
    test_deterministic_embedding_empty_text()
    test_retrieve_curated_fallback_inr()
    test_retrieve_curated_fallback_snad()
    test_vector_search_with_mock_es_store()
    print("=" * 65)
    print("ALL DAY 12 RAG PRECEDENT RETRIEVER TESTS PASSED (5/5)")
    print("=" * 65)


if __name__ == "__main__":
    run_all_tests()
