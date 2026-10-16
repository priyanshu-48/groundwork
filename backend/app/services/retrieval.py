import dataclasses
import uuid
from collections.abc import Hashable
from typing import Literal, get_args

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import DocKind
from app.repositories import chunks as chunks_repo
from app.repositories.chunks import Hit
from app.services.embeddings import EmbeddingProvider
from app.services.rerank import Reranker

Mode = Literal["vector", "hybrid", "hybrid_rerank"]


def rrf_fuse[K: Hashable](rank_lists: list[list[K]], k: int = 60) -> list[tuple[K, float]]:
    """Reciprocal Rank Fusion: score(item) = sum over lists of 1 / (k + rank).

    Only ranks are used, never the raw scores, which is what lets a cosine similarity (0..1) and a
    ts_rank_cd value (unbounded) be combined without any calibration. An item both lists like
    beats one that only a single list ranks first. Ties keep first-seen order (stable sort)."""
    scores: dict[K, float] = {}
    for ranked in rank_lists:
        for rank, item in enumerate(ranked, start=1):
            scores[item] = scores.get(item, 0.0) + 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda kv: kv[1], reverse=True)


async def search_documents(
    session: AsyncSession,
    embedder: EmbeddingProvider,
    org_id: uuid.UUID,
    query: str,
    *,
    mode: Mode,
    kind: DocKind | None = None,
    top_k: int = 5,
    reranker: Reranker | None = None,
    candidate_k: int = 20,
    rrf_k: int = 60,
) -> list[Hit]:
    """Hit.score depends on the mode: cosine similarity (vector), RRF score (hybrid), or the
    cross-encoder's relevance score (hybrid_rerank). Compare scores only within one mode."""
    if mode not in get_args(Mode):
        raise ValueError(f"unknown mode {mode!r}; expected one of {get_args(Mode)}")
    if mode == "hybrid_rerank" and reranker is None:
        raise ValueError("mode 'hybrid_rerank' needs a reranker")

    (vector,) = await embedder.embed([query], "query")
    if mode == "vector":
        return await chunks_repo.vector_search(session, org_id, vector, kind, top_k)

    by_vector = await chunks_repo.vector_search(session, org_id, vector, kind, candidate_k)
    by_keyword = await chunks_repo.keyword_search(session, org_id, query, kind, candidate_k)
    pool = {h.chunk_id: h for h in [*by_vector, *by_keyword]}
    fused = rrf_fuse([[h.chunk_id for h in by_vector], [h.chunk_id for h in by_keyword]], rrf_k)
    candidates = [dataclasses.replace(pool[cid], score=s) for cid, s in fused[:candidate_k]]
    if mode == "hybrid":
        return candidates[:top_k]
    assert reranker is not None
    return await reranker.rerank(query, candidates, top_k)


__all__ = ["Hit", "Mode", "rrf_fuse", "search_documents"]
