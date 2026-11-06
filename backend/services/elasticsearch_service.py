"""
DisputeShield AI — Elasticsearch Vector & Search Service

Handles index management, document indexing, full-text multi-match search,
and kNN dense vector search (cosine similarity) for RAG dispute resolution.
Includes an in-memory fallback engine for local testing when Elasticsearch is offline.
"""

import logging
import math
from typing import Any, Dict, List, Optional
from elasticsearch import AsyncElasticsearch, exceptions as es_exceptions

from config import settings

logger = logging.getLogger(__name__)


def _cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two numeric vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class ElasticsearchService:
    """
    Elasticsearch Service supporting full-text query, ES|QL analytics,
    and kNN dense vector similarity search.
    """

    DEFAULT_INDEX = "disputes_v1"
    VECTOR_DIM = 1536  # Standard dimension for OpenAI text-embedding-3-small

    def __init__(
        self,
        hosts: Optional[str] = None,
        index_name: Optional[str] = None,
        request_timeout: float = 1.0,
    ):
        self.hosts = hosts or settings.elasticsearch_url or "http://localhost:9200"
        self.index_name = index_name or settings.elasticsearch_index_disputes or self.DEFAULT_INDEX
        try:
            self.client = AsyncElasticsearch(
                hosts=[self.hosts],
                request_timeout=request_timeout,
                max_retries=0,
                retry_on_timeout=False,
            )
        except Exception as exc:
            logger.warning(f"Failed to initialize AsyncElasticsearch client: {exc}")
            self.client = None
        self.is_connected: Optional[bool] = None

        # In-memory mock store for test environments without live ES
        self._mock_store: Dict[str, Dict[str, Any]] = {}

    async def check_connection(self, force_refresh: bool = False) -> bool:
        """Ping Elasticsearch cluster to verify availability."""
        if not force_refresh and self.is_connected is not None:
            return self.is_connected

        if self.client is None:
            self.is_connected = False
            return False

        try:
            self.is_connected = bool(await self.client.ping())
        except Exception:
            self.is_connected = False
        return self.is_connected



    async def ensure_index(self, index_name: Optional[str] = None) -> bool:
        """
        Create the dispute index with dense_vector and full-text mappings if not present.
        """
        idx = index_name or self.index_name

        mappings = {
            "properties": {
                "dispute_id": {"type": "keyword"},
                "reason": {
                    "type": "text",
                    "fields": {"keyword": {"type": "keyword"}},
                },
                "status": {"type": "keyword"},
                "outcome": {"type": "keyword"},
                "amount": {"type": "float"},
                "buyer_message": {"type": "text"},
                "evidence_summary": {"type": "text"},
                "dispute_vector": {
                    "type": "dense_vector",
                    "dims": self.VECTOR_DIM,
                    "index": True,
                    "similarity": "cosine",
                },
                "created_at": {"type": "date"},
            }
        }

        if await self.check_connection():
            try:
                exists = await self.client.indices.exists(index=idx)
                if not exists:
                    await self.client.indices.create(index=idx, mappings=mappings)
                    logger.info(f"Created Elasticsearch index '{idx}' with dense_vector mappings.")
                return True
            except es_exceptions.ElasticsearchException as exc:
                logger.error(f"Failed to create Elasticsearch index: {exc}")
                return False
        else:
            logger.info(f"Using mock index '{idx}' (Elasticsearch unavailable).")
            return True

    async def index_dispute(
        self,
        dispute_data: Dict[str, Any],
        vector: Optional[List[float]] = None,
        index_name: Optional[str] = None,
    ) -> bool:
        """
        Index a dispute record with optional 1536-dim embedding vector.
        """
        idx = index_name or self.index_name
        doc_id = str(dispute_data.get("dispute_id") or dispute_data.get("paypal_dispute_id"))
        if not doc_id:
            raise ValueError("dispute_id or paypal_dispute_id is required")

        doc = {
            "dispute_id": doc_id,
            "reason": dispute_data.get("reason", "OTHER"),
            "status": dispute_data.get("status", "OPEN"),
            "amount": float(dispute_data.get("dispute_amount") or dispute_data.get("amount") or 0.0),
            "buyer_message": dispute_data.get("buyer_message") or "",
            "evidence_summary": dispute_data.get("evidence_summary") or dispute_data.get("agent_reasoning") or "",
            "outcome": dispute_data.get("outcome", "PENDING"),
            "created_at": dispute_data.get("created_at"),
        }
        if vector is not None:
            doc["dispute_vector"] = vector

        # Always save to mock store for reliable fallback
        self._mock_store[doc_id] = doc

        if await self.check_connection():
            try:
                await self.client.index(index=idx, id=doc_id, document=doc)
                return True
            except Exception as exc:
                logger.warning(f"Elasticsearch indexing failed: {exc}; stored in mock fallback.")
                return True
        return True

    async def search_disputes(
        self,
        query: str,
        reason: Optional[str] = None,
        size: int = 10,
        index_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Full-text multi-match search over buyer messages and evidence notes.
        """
        idx = index_name or self.index_name

        if await self.check_connection():
            body: Dict[str, Any] = {
                "size": size,
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["buyer_message^2", "evidence_summary", "reason"],
                                }
                            }
                        ],
                        "filter": [],
                    }
                },
            }
            if reason:
                body["query"]["bool"]["filter"].append({"term": {"reason.keyword": reason}})

            try:
                res = await self.client.search(index=idx, body=body)
                return [hit["_source"] for hit in res["hits"]["hits"]]
            except Exception as exc:
                logger.warning(f"Elasticsearch search failed: {exc}; running mock search.")

        # In-memory mock search
        results = []
        q_lower = query.lower()
        for doc in self._mock_store.values():
            if reason and doc.get("reason") != reason:
                continue
            text_corpus = f"{doc.get('buyer_message', '')} {doc.get('evidence_summary', '')} {doc.get('reason', '')}".lower()
            if q_lower in text_corpus:
                results.append(doc)
            if len(results) >= size:
                break
        return results

    async def vector_search(
        self,
        vector: List[float],
        k: int = 5,
        reason: Optional[str] = None,
        index_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform kNN dense vector search for similar past dispute resolutions.
        """
        idx = index_name or self.index_name

        if await self.check_connection():
            knn_query: Dict[str, Any] = {
                "field": "dispute_vector",
                "query_vector": vector,
                "k": k,
                "num_candidates": max(k * 5, 20),
            }
            if reason:
                knn_query["filter"] = {"term": {"reason.keyword": reason}}

            try:
                res = await self.client.search(index=idx, knn=knn_query, size=k)
                hits = []
                for hit in res["hits"]["hits"]:
                    src = hit["_source"]
                    src["_score"] = hit.get("_score")
                    hits.append(src)
                return hits
            except Exception as exc:
                logger.warning(f"Elasticsearch kNN query failed: {exc}; running mock vector search.")

        # In-memory mock vector cosine search
        scored_docs = []
        for doc in self._mock_store.values():
            if reason and doc.get("reason") != reason:
                continue
            doc_vec = doc.get("dispute_vector")
            if doc_vec:
                sim = _cosine_similarity(vector, doc_vec)
                doc_copy = dict(doc)
                doc_copy["_score"] = round(sim, 4)
                scored_docs.append(doc_copy)

        scored_docs.sort(key=lambda x: x.get("_score", 0.0), reverse=True)
        return scored_docs[:k]

    async def close(self) -> None:
        """Close the underlying Elasticsearch client."""
        if self.client:
            try:
                await self.client.close()
            except Exception:
                pass

