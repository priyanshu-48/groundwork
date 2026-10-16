import uuid
from pathlib import Path
from typing import get_args

import pytest

from app.models.document import DocKind
from app.repositories import chunks as chunks_repo
from app.repositories.chunks import Hit
from app.services.embeddings import FakeEmbeddingProvider
from app.services.rerank import FakeReranker
from app.services.retrieval import Mode, search_documents
from app.worker.deps import Deps
from tests.helpers import ingest_corpus, new_org


class UnrelatedQueryEmbedder(FakeEmbeddingProvider):
    """Query vectors point nowhere useful, so only keyword search can find the right chunk."""

    async def embed(self, texts: list[str], task: str) -> list[list[float]]:  # type: ignore[override]
        v = [0.0] * 768
        v[7] = 1.0
        return [v for _ in texts]


class RecordingReranker:
    def __init__(self) -> None:
        self.seen: list[Hit] = []

    async def rerank(self, query: str, hits: list[Hit], top_k: int) -> list[Hit]:
        self.seen = list(hits)
        return list(reversed(hits))[:top_k]  # a recognisable, non-trivial order


@pytest.fixture
async def corpus(deps: Deps, small: tuple[dict, Path]) -> tuple[uuid.UUID, dict]:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    return org, gt


async def test_keyword_finds_an_invoice_by_its_exact_number(
    deps: Deps, corpus: tuple[uuid.UUID, dict]
) -> None:
    org, gt = corpus
    target = gt["invoices"][5]
    async with deps.maker() as s:
        hits = await chunks_repo.keyword_search(s, org, target["invoice_number"], None, 5)
    assert hits and hits[0].filename == target["filename"]


async def test_keyword_uses_or_semantics_so_one_unmatched_word_does_not_zero_the_result(
    deps: Deps, corpus: tuple[uuid.UUID, dict]
) -> None:
    org, gt = corpus
    target = gt["invoices"][2]
    async with deps.maker() as s:
        hits = await chunks_repo.keyword_search(
            s, org, f"{target['invoice_number']} zzzqqq banana", None, 5
        )
    assert hits and hits[0].filename == target["filename"]


@pytest.mark.parametrize("q", ['"unbalanced', "-", ":*", "!!!", "a & | b", "\\", "'", "", "   "])
async def test_keyword_survives_odd_input(
    deps: Deps, corpus: tuple[uuid.UUID, dict], q: str
) -> None:
    org, _ = corpus
    async with deps.maker() as s:
        assert isinstance(await chunks_repo.keyword_search(s, org, q, None, 5), list)


async def test_keyword_stop_words_only_returns_nothing(
    deps: Deps, corpus: tuple[uuid.UUID, dict]
) -> None:
    org, _ = corpus
    async with deps.maker() as s:
        assert await chunks_repo.keyword_search(s, org, "what is the", None, 5) == []


async def test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(
    deps: Deps, corpus: tuple[uuid.UUID, dict]
) -> None:
    org, gt = corpus
    target = gt["invoices"][7]
    async with deps.maker() as s:
        hits = await search_documents(
            s, UnrelatedQueryEmbedder(), org, target["invoice_number"], mode="hybrid", top_k=3
        )
    assert target["filename"] in [h.filename for h in hits]


async def test_rerank_mode_follows_the_reranker_and_limits_candidates(
    deps: Deps, corpus: tuple[uuid.UUID, dict]
) -> None:
    org, _ = corpus
    rr = RecordingReranker()
    async with deps.maker() as s:
        out = await search_documents(
            s, deps.embedder, org, "liability cap", mode="hybrid_rerank", top_k=4, reranker=rr
        )
    assert 0 < len(rr.seen) <= 20
    assert len(out) == 4
    assert [h.chunk_id for h in out] == [h.chunk_id for h in list(reversed(rr.seen))[:4]]


async def test_rerank_mode_requires_a_reranker(deps: Deps, corpus: tuple[uuid.UUID, dict]) -> None:
    org, _ = corpus
    async with deps.maker() as s:
        with pytest.raises(ValueError, match="reranker"):
            await search_documents(s, deps.embedder, org, "q", mode="hybrid_rerank")


async def test_unknown_mode_is_rejected(deps: Deps, corpus: tuple[uuid.UUID, dict]) -> None:
    org, _ = corpus
    async with deps.maker() as s:
        with pytest.raises(ValueError, match="mode"):
            await search_documents(s, deps.embedder, org, "q", mode="bm25")  # type: ignore[arg-type]


@pytest.mark.parametrize("mode", get_args(Mode))
async def test_every_mode_respects_org_isolation_and_kind(
    deps: Deps, corpus: tuple[uuid.UUID, dict], mode: str
) -> None:
    org, _ = corpus
    stranger = await new_org(deps)
    kwargs = dict(mode=mode, reranker=FakeReranker())
    async with deps.maker() as s:
        assert await search_documents(s, deps.embedder, stranger, "liability cap", **kwargs) == []  # type: ignore[arg-type]
        inv = await search_documents(
            s,
            deps.embedder,
            org,
            "invoice total",
            kind=DocKind.invoice,
            top_k=5,
            **kwargs,  # type: ignore[arg-type]
        )
        con = await search_documents(
            s,
            deps.embedder,
            org,
            "invoice total",
            kind=DocKind.contract,
            top_k=5,
            **kwargs,  # type: ignore[arg-type]
        )
    assert inv and all(h.filename.startswith("invoice_") for h in inv)
    assert con and all(h.filename.startswith("contract_") for h in con)
