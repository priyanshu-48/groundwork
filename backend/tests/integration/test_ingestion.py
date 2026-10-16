import dataclasses
from decimal import Decimal

import pytest

from app.services import ingestion
from app.services.chunking import chunk_pages
from app.services.embeddings import FakeEmbeddingProvider
from app.services.parsing import extract_pages
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import invoice_text, make_due, make_pdf, new_org, rows, scalar, seed, words


async def _chunks(deps: Deps, doc_id: object) -> int:
    return int(await scalar(deps, "SELECT count(*) FROM chunks WHERE document_id = :d", d=doc_id))


async def _doc(deps: Deps, doc_id: object) -> dict[str, object]:
    return dict((await rows(deps, "SELECT * FROM documents WHERE id = :d", d=doc_id))[0])


async def test_pdf_becomes_ready_with_chunks_and_embeddings(deps: Deps) -> None:
    org = await new_org(deps)
    pdf = make_pdf([words(800, "alpha"), words(300, "beta")])
    doc_id = await seed(deps, org, pdf)
    expected = len(chunk_pages(extract_pages(pdf, 200)))
    assert expected > 2

    assert await process_one(deps, "w1") is True

    doc = await _doc(deps, doc_id)
    assert doc["status"] == "ready" and doc["page_count"] == 2 and doc["error"] is None
    assert await _chunks(deps, doc_id) == expected
    bad = await scalar(
        deps,
        "SELECT count(*) FROM chunks WHERE document_id = :d AND "
        "(embedding IS NULL OR vector_dims(embedding) <> 768 OR tsv = ''::tsvector "
        "OR org_id <> :o)",
        d=doc_id,
        o=org,
    )
    assert bad == 0
    assert await scalar(deps, "SELECT status FROM jobs") == "done"
    assert await process_one(deps, "w1") is False  # queue drained


async def test_crash_before_commit_leaves_nothing_and_rerun_has_no_duplicates(
    deps: Deps, monkeypatch: pytest.MonkeyPatch
) -> None:
    org = await new_org(deps)
    pdf = make_pdf([invoice_text(filler=words(700))])
    doc_id = await seed(deps, org, pdf, "invoice")
    expected = len(chunk_pages(extract_pages(pdf, 200)))

    async def killed(*_a: object, **_k: object) -> None:
        raise RuntimeError("worker killed after chunks were inserted, before commit")

    monkeypatch.setattr(ingestion, "_store_invoice", killed)
    await process_one(deps, "w1")
    assert await _chunks(deps, doc_id) == 0  # the whole write transaction rolled back
    assert (await _doc(deps, doc_id))["status"] == "processing"
    assert await scalar(deps, "SELECT status FROM jobs") == "queued"  # will be retried

    monkeypatch.undo()
    await make_due(deps)
    await process_one(deps, "w2")
    assert await _chunks(deps, doc_id) == expected  # exactly once: 0 lost, 0 duplicated
    assert (await _doc(deps, doc_id))["status"] == "ready"
    assert await scalar(deps, "SELECT count(*) FROM invoices WHERE document_id = :d", d=doc_id) == 1


async def test_crash_during_embedding_then_rerun(deps: Deps) -> None:
    class FlakyOnce(FakeEmbeddingProvider):
        failed = False

        async def embed(self, texts: list[str], task: str) -> list[list[float]]:  # type: ignore[override]
            if not self.failed:
                self.failed = True
                raise RuntimeError("process died mid-embedding")
            return await super().embed(texts, task)  # type: ignore[arg-type]

    flaky = dataclasses.replace(deps, embedder=FlakyOnce())
    org = await new_org(deps)
    pdf = make_pdf([words(700)])
    doc_id = await seed(deps, org, pdf)
    expected = len(chunk_pages(extract_pages(pdf, 200)))

    await process_one(flaky, "w1")
    assert await _chunks(deps, doc_id) == 0
    await make_due(deps)
    await process_one(flaky, "w1")
    assert await _chunks(deps, doc_id) == expected


async def test_redelivery_after_success_replaces_not_appends(deps: Deps) -> None:
    org = await new_org(deps)
    pdf = make_pdf([words(900)])
    doc_id = await seed(deps, org, pdf)
    expected = len(chunk_pages(extract_pages(pdf, 200)))
    await process_one(deps, "w1")
    await ingestion.ingest_document(deps, doc_id)  # e.g. reaper requeued a job that had finished
    await ingestion.ingest_document(deps, doc_id)
    assert await _chunks(deps, doc_id) == expected


async def test_invoice_with_good_totals_is_stored_clean(deps: Deps) -> None:
    org = await new_org(deps)
    doc_id = await seed(deps, org, make_pdf([invoice_text()]), "invoice")
    await process_one(deps, "w1")
    (inv,) = await rows(deps, "SELECT * FROM invoices WHERE document_id = :d", d=doc_id)
    assert inv["needs_review"] is False and inv["review_reason"] is None
    assert inv["total"] == Decimal("110.00") and inv["vendor"] == "Acme Corp"
    assert inv["org_id"] == org


async def test_invoice_with_bad_totals_is_flagged_not_trusted(deps: Deps) -> None:
    org = await new_org(deps)
    doc_id = await seed(deps, org, make_pdf([invoice_text(total="999.00")]), "invoice")
    await process_one(deps, "w1")
    (inv,) = await rows(deps, "SELECT * FROM invoices WHERE document_id = :d", d=doc_id)
    assert inv["needs_review"] is True and "subtotal" in inv["review_reason"]
    assert (await _doc(deps, doc_id))["status"] == "ready"  # text stays searchable


async def test_duplicate_invoice_number_is_flagged(deps: Deps) -> None:
    org = await new_org(deps)
    first = await seed(deps, org, make_pdf([invoice_text(filler="one")]), "invoice")
    second = await seed(deps, org, make_pdf([invoice_text(filler="two")]), "invoice")
    await process_one(deps, "w1")
    await process_one(deps, "w1")
    flags = {
        r["document_id"]: r["needs_review"]
        for r in await rows(deps, "SELECT * FROM invoices WHERE org_id = :o", o=org)
    }
    assert flags == {first: False, second: True}


async def test_corrupt_pdf_fails_permanently_without_retries(deps: Deps) -> None:
    org = await new_org(deps)
    doc_id = await seed(deps, org, b"%PDF-1.4 this is not really a pdf")
    await process_one(deps, "w1")
    doc = await _doc(deps, doc_id)
    assert doc["status"] == "failed" and doc["error"]
    (job,) = await rows(deps, "SELECT status, attempts FROM jobs")
    assert (job["status"], job["attempts"]) == ("failed", 1)


async def test_pdf_without_text_fails_permanently(deps: Deps) -> None:
    org = await new_org(deps)
    doc_id = await seed(deps, org, make_pdf([""]))
    await process_one(deps, "w1")
    assert (await _doc(deps, doc_id))["status"] == "failed"


async def test_transient_failures_end_in_failed_document_after_max_attempts(deps: Deps) -> None:
    class AlwaysDown(FakeEmbeddingProvider):
        async def embed(self, texts: list[str], task: str) -> list[list[float]]:  # type: ignore[override]
            raise RuntimeError("gemini is down")

    down = dataclasses.replace(deps, embedder=AlwaysDown())
    org = await new_org(deps)
    doc_id = await seed(deps, org, make_pdf([words(50)]))
    for _ in range(5):
        await process_one(down, "w1")
        await make_due(deps)
    doc = await _doc(deps, doc_id)
    assert doc["status"] == "failed" and "gemini is down" in str(doc["error"])
    (job,) = await rows(deps, "SELECT status, attempts FROM jobs")
    assert (job["status"], job["attempts"]) == ("failed", 5)


async def test_search_indexes_exist(deps: Deps) -> None:
    defs = " ".join(
        r["indexdef"]
        for r in await rows(deps, "SELECT indexdef FROM pg_indexes WHERE tablename='chunks'")
    )
    assert "hnsw" in defs and "vector_cosine_ops" in defs and "gin" in defs
