import dataclasses

from app.services.extraction import FakeInvoiceExtractor, InvoiceFields
from app.worker.backfill_invoices import backfill
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import invoice_text, make_pdf, new_org, rows, scalar, seed


class CountingExtractor(FakeInvoiceExtractor):
    def __init__(self) -> None:
        self.many_calls = 0
        self.seen_texts: list[str] = []

    async def extract_many(self, texts: list[str]) -> list[InvoiceFields]:
        self.many_calls += 1
        self.seen_texts += texts
        return await super().extract_many(texts)


async def ingest_without_extraction(
    deps: Deps, org: object, n: int, bad_total_at: int = -1
) -> None:
    off = dataclasses.replace(
        deps, settings=deps.settings.model_copy(update={"extraction_enabled": False})
    )
    for i in range(n):
        total = "999.00" if i == bad_total_at else "110.00"
        pdf = make_pdf([invoice_text(number=f"BF-{i:03d}", total=total, filler=f"line {i}")])
        await seed(deps, org, pdf, "invoice")  # type: ignore[arg-type]
    while await process_one(off, "w"):
        pass


async def test_backfill_extracts_ten_per_call_flags_bad_totals_and_is_idempotent(
    deps: Deps,
) -> None:
    org = await new_org(deps)
    await ingest_without_extraction(deps, org, 12, bad_total_at=4)
    assert await scalar(deps, "SELECT count(*) FROM invoices WHERE org_id = :o", o=org) == 0
    counting = CountingExtractor()
    d = dataclasses.replace(deps, extractor=counting)

    result = await backfill(d, batch_size=10)

    assert (result.documents, result.llm_calls, result.flagged) == (12, 2, 1)
    assert counting.many_calls == 2  # 12 invoices, 2 requests
    found = await rows(
        deps, "SELECT invoice_number, needs_review FROM invoices WHERE org_id = :o", o=org
    )
    assert len(found) == 12
    assert [r["invoice_number"] for r in found if r["needs_review"]] == ["BF-004"]

    again = await backfill(d, batch_size=10)
    assert (again.documents, again.llm_calls) == (0, 0)  # nothing left, no wasted LLM call
    assert counting.many_calls == 2


async def test_backfill_limit_stops_early_and_resumes(deps: Deps) -> None:
    org = await new_org(deps)
    await ingest_without_extraction(deps, org, 5)
    counting = CountingExtractor()
    d = dataclasses.replace(deps, extractor=counting)
    first = await backfill(d, batch_size=2, limit=3)
    assert first.documents == 3 and counting.many_calls == 2  # batches of 2 then 1
    rest = await backfill(d, batch_size=2)
    assert rest.documents == 2
    assert await scalar(deps, "SELECT count(*) FROM invoices WHERE org_id = :o", o=org) == 5


async def test_backfill_ignores_contracts_and_documents_still_processing(deps: Deps) -> None:
    org = await new_org(deps)
    await seed(deps, org, make_pdf(["Payment Terms. Net 30."]), "contract")
    await seed(
        deps, org, make_pdf([invoice_text(number="PENDING-1")]), "invoice"
    )  # never processed
    counting = CountingExtractor()
    result = await backfill(dataclasses.replace(deps, extractor=counting), batch_size=10)
    assert result.documents == 0 and counting.many_calls == 0


async def test_retry_flagged_reextracts_once_per_run_without_looping(deps: Deps) -> None:
    org = await new_org(deps)
    await ingest_without_extraction(deps, org, 3, bad_total_at=1)
    counting = CountingExtractor()
    d = dataclasses.replace(deps, extractor=counting)
    await backfill(d, batch_size=10)
    assert counting.many_calls == 1

    assert (await backfill(d, batch_size=10)).documents == 0  # default: flagged rows are left alone

    counting.seen_texts.clear()
    await backfill(d, batch_size=10, retry_flagged=True)
    # Other tests leave flagged rows of their own orgs in the shared DB (the backfill is an
    # org-agnostic operator tool), so look only at our flagged document: once, not repeatedly.
    ours = [t for t in counting.seen_texts if "BF-001" in t]
    assert len(ours) == 1
