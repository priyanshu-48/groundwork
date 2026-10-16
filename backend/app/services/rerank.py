"""Second-stage reranking. A cross-encoder reads the query and one chunk together, so it can judge
relevance far more precisely than the embedding model (which encodes them separately), but it is
too slow to run over the whole corpus. Hence: cheap retrieval first, expensive rerank on ~20."""

import asyncio
import dataclasses
import re
from typing import Any, Protocol

from app.repositories.chunks import Hit

DEFAULT_MODEL = "ms-marco-MiniLM-L-12-v2"  # keep in sync with the Dockerfile pre-download


class Reranker(Protocol):
    async def rerank(self, query: str, hits: list[Hit], top_k: int) -> list[Hit]: ...


_WORD = re.compile(r"[a-z0-9]+")


class FakeReranker:
    """Scores by how many distinct query words a chunk contains. Offline stand-in for tests."""

    async def rerank(self, query: str, hits: list[Hit], top_k: int) -> list[Hit]:
        q = set(_WORD.findall(query.lower()))
        scored = [
            dataclasses.replace(h, score=float(len(q & set(_WORD.findall(h.content.lower())))))
            for h in hits
        ]
        return sorted(scored, key=lambda h: h.score, reverse=True)[:top_k]


class FlashRankReranker:
    """FlashRank cross-encoder (ONNX, CPU, no PyTorch). max_length=512 so our ~500-token chunks
    are not truncated; FlashRank's older 128 default would cut off most of a chunk."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
        cache_dir: str = ".flashrank",
        max_length: int = 512,
        ranker: Any = None,
    ) -> None:
        if ranker is None:
            from flashrank import Ranker

            ranker = Ranker(model_name=model_name, cache_dir=cache_dir, max_length=max_length)
        self._ranker = ranker

    async def rerank(self, query: str, hits: list[Hit], top_k: int) -> list[Hit]:
        if not hits:
            return []
        from flashrank import RerankRequest

        request = RerankRequest(
            query=query, passages=[{"id": i, "text": h.content} for i, h in enumerate(hits)]
        )
        results = await asyncio.to_thread(self._ranker.rerank, request)  # CPU-bound: off the loop
        ranked = sorted(results, key=lambda r: r["score"], reverse=True)[:top_k]
        return [dataclasses.replace(hits[r["id"]], score=float(r["score"])) for r in ranked]
