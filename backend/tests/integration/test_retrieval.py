from pathlib import Path

import pytest
from evals.generate_corpus import build_ground_truth, render_corpus

from app.models.document import DocKind
from app.services.embeddings import FakeEmbeddingProvider
from app.services.retrieval import search_documents
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import new_org, seed


@pytest.fixture(scope="module")
def small(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict, Path]:
    out = tmp_path_factory.mktemp("retrieval-corpus")
    gt = build_ground_truth(seed=42, n_vendors=6, n_invoices=24)
    render_corpus(gt, out, seed=42)
    return gt, out


async def ingest(deps: Deps, org: object, gt: dict, out: Path) -> None:
    for v in gt["vendors"]:
        name = v["contract"]["filename"]
        await seed(deps, org, (out / "contracts" / name).read_bytes(), "contract", name)  # type: ignore[arg-type]
    for inv in gt["invoices"]:
        name = inv["filename"]
        await seed(deps, org, (out / "invoices" / name).read_bytes(), "invoice", name)  # type: ignore[arg-type]
    while await process_one(deps, "w"):
        pass


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
    await ingest(deps, org, gt, out)
    doc_hits = page_hits = 0
    for v in gt["vendors"]:
        fact = v["contract"]["facts"]["liability_cap"]
        async with deps.maker() as s:
            hits = await search_documents(
                s,
                deps.embedder,
                org,
                f"What is the liability cap in the {v['name']} contract?",
                top_k=5,  # type: ignore[arg-type]
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
    await ingest(deps, org, gt, out)
    q = "payment terms net days invoice"
    async with deps.maker() as s:
        hits = await search_documents(s, deps.embedder, org, q, top_k=8)  # type: ignore[arg-type]
        contracts = await search_documents(s, deps.embedder, org, q, kind=DocKind.contract, top_k=8)  # type: ignore[arg-type]
        invoices = await search_documents(s, deps.embedder, org, q, kind=DocKind.invoice, top_k=3)  # type: ignore[arg-type]
    assert len(hits) == 8
    assert [h.score for h in hits] == sorted((h.score for h in hits), reverse=True)
    assert all(h.filename.startswith("contract_") for h in contracts) and contracts
    assert len(invoices) == 3 and all(h.filename.startswith("invoice_") for h in invoices)
    assert hits[0].page >= 1 and hits[0].content


async def test_another_org_sees_nothing(deps: Deps, small: tuple[dict, Path]) -> None:
    gt, out = small
    owner, stranger = await new_org(deps), await new_org(deps)
    await ingest(deps, owner, gt, out)
    async with deps.maker() as s:
        assert await search_documents(s, deps.embedder, stranger, "liability cap", top_k=5) == []  # type: ignore[arg-type]


async def test_query_is_embedded_with_the_query_task(deps: Deps) -> None:
    rec = Recording()
    org = await new_org(deps)
    async with deps.maker() as s:
        await search_documents(s, rec, org, "anything", top_k=1)  # type: ignore[arg-type]
    assert rec.tasks == ["query"]
