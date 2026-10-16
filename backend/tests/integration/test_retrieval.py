from pathlib import Path

from app.models.document import DocKind
from app.services.embeddings import FakeEmbeddingProvider
from app.services.retrieval import search_documents
from app.worker.deps import Deps
from tests.helpers import ingest_corpus, new_org


class Recording(FakeEmbeddingProvider):
    tasks: list[str]

    def __init__(self) -> None:
        super().__init__()
        self.tasks = []

    async def embed(self, texts: list[str], task: str) -> list[list[float]]:  # type: ignore[override]
        self.tasks.append(task)
        return await super().embed(texts, task)  # type: ignore[arg-type]


async def test_questions_find_their_contract_and_mostly_their_page(
    deps: Deps, small: tuple[dict, Path]
) -> None:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    doc_hits = page_hits = 0
    for v in gt["vendors"]:
        fact = v["contract"]["facts"]["liability_cap"]
        async with deps.maker() as s:
            hits = await search_documents(
                s,
                deps.embedder,
                org,
                f"What is the liability cap in the {v['name']} contract?",
                mode="vector",
                top_k=5,
            )
        doc_hits += any(h.filename == v["contract"]["filename"] for h in hits)
        page_hits += any(
            h.filename == v["contract"]["filename"] and h.page == fact["page"] for h in hits
        )
    assert doc_hits == 6 and page_hits >= 5


async def test_results_are_ranked_capped_and_filterable(
    deps: Deps, small: tuple[dict, Path]
) -> None:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    q = "payment terms net days invoice"
    async with deps.maker() as s:
        hits = await search_documents(s, deps.embedder, org, q, mode="vector", top_k=8)
        contracts = await search_documents(
            s, deps.embedder, org, q, mode="vector", kind=DocKind.contract, top_k=8
        )
        invoices = await search_documents(
            s, deps.embedder, org, q, mode="vector", kind=DocKind.invoice, top_k=3
        )
    assert len(hits) == 8
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)
    assert all(h.filename.startswith("contract_") for h in contracts) and contracts
    assert len(invoices) == 3 and all(h.filename.startswith("invoice_") for h in invoices)
    assert hits[0].page >= 1 and hits[0].content


async def test_another_org_sees_nothing(deps: Deps, small: tuple[dict, Path]) -> None:
    gt, out = small
    owner, stranger = await new_org(deps), await new_org(deps)
    await ingest_corpus(deps, owner, gt, out)
    async with deps.maker() as s:
        hits = await search_documents(
            s, deps.embedder, stranger, "liability cap", mode="vector", top_k=5
        )
    assert hits == []


async def test_query_is_embedded_with_the_query_task(deps: Deps) -> None:
    rec = Recording()
    org = await new_org(deps)
    async with deps.maker() as s:
        await search_documents(s, rec, org, "anything", mode="vector", top_k=1)
    assert rec.tasks == ["query"]
