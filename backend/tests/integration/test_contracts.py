import dataclasses
import json
import uuid
from decimal import Decimal
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import text

from app.agent.llm import FakeLLM, call, say
from app.agent.loop import run_agent
from app.agent.tools import AgentContext, execute
from app.models.contract import Contract
from app.models.document import DocKind, DocStatus, Document
from app.services import ingestion
from app.services.contract_extraction import ContractFields
from app.services.extraction import FakeInvoiceExtractor
from app.worker.backfill_contracts import backfill
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import add_invoice_row, ingest_corpus, make_due, new_org, rows, scalar, seed


def contract_text(
    vendor: str, terms: int, renew: bool = True, law: str = "State of Delaware"
) -> str:
    renewal = "renews automatically" if renew else "does not renew automatically"
    return (
        f"This Master Services Agreement is made between {vendor} (the Supplier), and Client. "
        f"Payment Terms. Client shall pay within {terms} ({terms}) days (Net {terms}). "
        "Late Payment. A late fee of 1.5% per month applies. "
        "Termination for Convenience. Either party may end this by giving sixty (60) days' "
        f"written notice. Term and Renewal. This Agreement {renewal}. "
        "Limitation of Liability. Liability shall not exceed USD 250,000. "
        f"Governing Law. This Agreement is governed by the laws of the {law}, without regard to "
        "its conflict-of-law principles."
    )


async def add_contract(
    deps: Deps, org: uuid.UUID, vendor: str, terms: int, review: bool = False, **kw: Any
) -> None:
    from app.models.contract import Contract as C

    async with deps.maker.begin() as s:
        doc = Document(
            org_id=org,
            filename=f"contract_{vendor}.pdf",
            s3_key=f"k/{vendor}",
            sha256=uuid.uuid4().hex + uuid.uuid4().hex,
            kind=DocKind.contract,
            status=DocStatus.ready,
        )
        s.add(doc)
        await s.flush()
        s.add(
            C(
                org_id=org,
                document_id=doc.id,
                vendor=vendor,
                payment_terms_days=terms,
                late_fee_percent=Decimal("1.5"),
                termination_notice_days=60,
                auto_renewal=kw.get("renew", True),
                liability_cap_amount=Decimal("250000"),
                liability_cap_currency="USD",
                governing_law=kw.get("law", "State of Delaware"),
                needs_review=review,
                review_reason="test" if review else None,
            )
        )


def ctx_for(deps: Deps, org: uuid.UUID) -> AgentContext:
    return AgentContext(org, deps.maker, deps.embedder, deps.settings)


async def q(deps: Deps, org: uuid.UUID, tool: str, **args: Any) -> dict[str, Any]:
    out = await execute(ctx_for(deps, org), tool, args)
    assert not out.is_error, out.text
    return json.loads(out.text)  # type: ignore[no-any-return]


# ------------------------------------------------------------------ ingestion


async def test_ingesting_a_contract_stores_its_structured_facts(deps: Deps) -> None:
    org = await new_org(deps)
    from tests.helpers import make_pdf

    doc_id = await seed(deps, org, make_pdf([contract_text("Acme Labs", 45)]), "contract")
    await process_one(deps, "w")
    (c,) = await rows(deps, "SELECT * FROM contracts WHERE document_id = :d", d=doc_id)
    assert (c["vendor"], c["payment_terms_days"], c["termination_notice_days"]) == (
        "Acme Labs",
        45,
        60,
    )
    assert c["late_fee_percent"] == Decimal("1.50") and c["auto_renewal"] is True
    assert (c["liability_cap_currency"], c["liability_cap_amount"]) == ("USD", Decimal("250000.00"))
    assert c["governing_law"] == "State of Delaware" and c["needs_review"] is False


async def test_reingest_replaces_the_row_instead_of_adding_another(deps: Deps) -> None:
    org = await new_org(deps)
    from tests.helpers import make_pdf

    doc_id = await seed(deps, org, make_pdf([contract_text("Acme Labs", 30)]), "contract")
    await process_one(deps, "w")
    await ingestion.ingest_document(deps, doc_id)
    await ingestion.ingest_document(deps, doc_id)
    assert (
        await scalar(deps, "SELECT count(*) FROM contracts WHERE document_id = :d", d=doc_id) == 1
    )


async def test_a_crash_before_commit_leaves_no_contract_row(
    deps: Deps, monkeypatch: pytest.MonkeyPatch
) -> None:
    org = await new_org(deps)
    from tests.helpers import make_pdf

    doc_id = await seed(deps, org, make_pdf([contract_text("Acme Labs", 30)]), "contract")

    async def killed(*_a: object, **_k: object) -> None:
        raise RuntimeError("killed after chunks, before commit")

    monkeypatch.setattr(ingestion, "_store_contract", killed)
    await process_one(deps, "w")
    assert (
        await scalar(deps, "SELECT count(*) FROM contracts WHERE document_id = :d", d=doc_id) == 0
    )
    assert await scalar(deps, "SELECT count(*) FROM chunks WHERE document_id = :d", d=doc_id) == 0
    monkeypatch.undo()
    await make_due(deps)
    await process_one(deps, "w")
    assert (
        await scalar(deps, "SELECT count(*) FROM contracts WHERE document_id = :d", d=doc_id) == 1
    )


async def test_a_contract_with_missing_facts_is_stored_flagged(deps: Deps) -> None:
    org = await new_org(deps)
    from tests.helpers import make_pdf

    doc_id = await seed(deps, org, make_pdf(["Some unrelated text about parking."]), "contract")
    await process_one(deps, "w")
    (c,) = await rows(
        deps, "SELECT needs_review, review_reason FROM contracts WHERE document_id = :d", d=doc_id
    )
    assert c["needs_review"] is True and "missing fields" in c["review_reason"]


async def test_extraction_off_skips_contract_rows_too(deps: Deps) -> None:
    off = dataclasses.replace(
        deps, settings=deps.settings.model_copy(update={"extraction_enabled": False})
    )
    org = await new_org(deps)
    from tests.helpers import make_pdf

    doc_id = await seed(deps, org, make_pdf([contract_text("Acme Labs", 30)]), "contract")
    await process_one(off, "w")
    assert (
        await scalar(deps, "SELECT count(*) FROM contracts WHERE document_id = :d", d=doc_id) == 0
    )


# ----------------------------------------------------------------- query_contracts


@pytest.fixture
async def org(deps: Deps) -> uuid.UUID:
    o = await new_org(deps)
    await add_contract(deps, o, "Acme Labs", 30)
    await add_contract(deps, o, "Globex Cloud", 45, renew=False, law="England and Wales")
    await add_contract(deps, o, "Initech Print", 30, law="State of New York")
    await add_contract(deps, o, "Hooli Media", 30, review=True)  # flagged: must stay invisible
    return o


async def test_query_contracts_filters_by_terms_renewal_and_law(deps: Deps, org: uuid.UUID) -> None:
    net30 = await q(deps, org, "query_contracts", payment_terms_days=30)
    assert [r["vendor"] for r in net30["rows"]] == ["Acme Labs", "Initech Print"]  # Hooli flagged
    assert [
        r["vendor"] for r in (await q(deps, org, "query_contracts", auto_renewal=False))["rows"]
    ] == ["Globex Cloud"]
    law = await q(deps, org, "query_contracts", governing_law="england")
    assert [r["vendor"] for r in law["rows"]] == ["Globex Cloud"]
    one = (await q(deps, org, "query_contracts", vendor="acme"))["rows"][0]
    assert one["payment_terms_days"] == 30 and one["liability_cap_amount"] == "250000.00"
    assert one["liability_cap_currency"] == "USD" and "document_id" not in one
    assert "ref" not in one  # structured rows have no page, so there is no citation handle


async def test_query_contracts_wildcards_are_literal_and_other_orgs_see_nothing(
    deps: Deps, org: uuid.UUID
) -> None:
    for evil in ["%", "_", "x'; DROP TABLE contracts; --"]:
        assert (await q(deps, org, "query_contracts", vendor=evil))["rows"] == []
    stranger = await new_org(deps)
    assert (await q(deps, stranger, "query_contracts"))["rows"] == []
    assert await scalar(deps, "SELECT count(*) FROM contracts") >= 4  # the table still exists


@pytest.mark.parametrize(
    "args",
    [
        {"payment_terms_days": 0},
        {"payment_terms_days": 999},
        {"limit": 51},
        {"org_id": "x"},
        {"sql": "x"},
    ],
)
async def test_query_contracts_rejects_bad_arguments(
    deps: Deps, org: uuid.UUID, args: dict[str, Any]
) -> None:
    out = await execute(ctx_for(deps, org), "query_contracts", args)
    assert out.is_error and out.text.startswith("Error: invalid arguments")


# ------------------------------------------- invoices filtered by their vendor's terms


async def test_invoices_can_be_filtered_by_the_vendors_contract_terms(
    deps: Deps, org: uuid.UUID
) -> None:
    await add_invoice_row(deps, org, "Acme Labs", "A-1", "2025-03-05", "100.00")
    await add_invoice_row(
        deps, org, "acme labs ", "A-2", "2025-03-06", "50.00"
    )  # case/space tolerant
    await add_invoice_row(deps, org, "Globex Cloud", "G-1", "2025-03-07", "900.00")
    await add_invoice_row(
        deps, org, "Hooli Media", "H-1", "2025-03-08", "700.00"
    )  # flagged contract
    await add_invoice_row(deps, org, "Initech Print", "I-1", "2025-04-09", "30.00")  # other month

    r = await q(deps, org, "query_invoices", aggregate="sum", payment_terms_days=30,
                date_from="2025-03-01", date_to="2025-03-31", group_by_vendor=True)  # fmt: skip
    got = {row["vendor"].strip().lower(): row["total"] for row in r["rows"]}
    assert got == {"acme labs": "150.00"}  # no Globex (net-45), no Hooli (flagged), no April

    total = await q(deps, org, "query_invoices", aggregate="sum", payment_terms_days=45)
    assert total["rows"][0]["total"] == "900.00"


async def test_two_contract_documents_for_one_vendor_do_not_double_count(deps: Deps) -> None:
    o = await new_org(deps)
    await add_contract(deps, o, "Acme Labs", 30)
    await add_contract(deps, o, "Acme Labs", 30)  # e.g. a re-uploaded amendment
    await add_invoice_row(deps, o, "Acme Labs", "A-1", "2025-03-05", "100.00")
    r = await q(deps, o, "query_invoices", aggregate="sum", payment_terms_days=30)
    assert r["rows"][0]["total"] == "100.00" and r["rows"][0]["invoice_count"] == 1


# ------------------------------------------------------------------- the agent


async def test_multi_hop_is_now_two_tool_calls_not_a_search_loop(
    deps: Deps, org: uuid.UUID
) -> None:
    await add_invoice_row(deps, org, "Acme Labs", "A-1", "2025-03-05", "100.00")
    await add_invoice_row(deps, org, "Initech Print", "I-1", "2025-03-06", "400.00")
    llm = FakeLLM(
        [
            call("query_contracts", payment_terms_days=30),
            call("query_invoices", aggregate="sum", payment_terms_days=30, group_by_vendor=True,
                 date_from="2025-03-01", date_to="2025-03-31"),
            say("Initech Print billed the most: USD 400.00."),
        ]
    )  # fmt: skip
    events = [
        e async for e in run_agent(ctx_for(deps, org), llm, "Which net-30 vendor billed most?")
    ]
    done = events[-1].data
    assert done["status"] == "ok" and [s["tool"] for s in done["steps"]] == [
        "query_contracts",
        "query_invoices",
    ]
    assert "Initech Print" in done["answer"]


# -------------------------------------------------------------------- backfill


class CountingExtractor(FakeInvoiceExtractor):
    def __init__(self) -> None:
        self.calls = 0

    async def extract_contracts_many(self, texts: list[str]) -> list[ContractFields]:
        self.calls += 1
        return await super().extract_contracts_many(texts)


async def test_backfill_extracts_three_per_call_and_is_idempotent(
    deps: Deps, small: tuple[dict, Path]
) -> None:
    gt, out = small
    org = await new_org(deps)
    off = dataclasses.replace(
        deps, settings=deps.settings.model_copy(update={"extraction_enabled": False})
    )
    from tests.helpers import make_pdf  # noqa: F401

    for v in gt["vendors"]:
        name = v["contract"]["filename"]
        await seed(deps, org, (out / "contracts" / name).read_bytes(), "contract", name)
    while await process_one(off, "w"):
        pass
    assert await scalar(deps, "SELECT count(*) FROM contracts WHERE org_id = :o", o=org) == 0

    counting = CountingExtractor()
    d = dataclasses.replace(deps, extractor=counting)
    r = await backfill(d)  # org-agnostic: other tests' contracts may be picked up too
    assert r.documents >= 6 and counting.calls >= 2
    mine = await rows(
        deps,
        "SELECT vendor, payment_terms_days, needs_review FROM contracts WHERE org_id = :o",
        o=org,
    )
    assert len(mine) == 6 and not any(m["needs_review"] for m in mine)
    by_name = {
        v["name"]: int(v["contract"]["facts"]["payment_terms"]["value"].split("-")[1])
        for v in gt["vendors"]
    }
    assert {m["vendor"]: m["payment_terms_days"] for m in mine} == by_name

    before = counting.calls
    again = await backfill(d)
    assert again.documents == 0 and counting.calls == before  # nothing left, no wasted LLM call


async def test_generated_corpus_ingests_with_every_fact_right(
    deps: Deps, small: tuple[dict, Path]
) -> None:
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, gt, out)
    got = {
        r["vendor"]: r for r in await rows(deps, "SELECT * FROM contracts WHERE org_id = :o", o=org)
    }
    for v in gt["vendors"]:
        f, c = v["contract"]["facts"], got[v["name"]]
        assert c["payment_terms_days"] == int(f["payment_terms"]["value"].split("-")[1])
        assert c["auto_renewal"] is (f["auto_renewal"]["value"] == "yes")
        assert c["governing_law"] == f["governing_law"]["value"] and not c["needs_review"]
    assert Contract.__tablename__ == "contracts"
    assert (
        await scalar(
            deps, "SELECT count(*) FROM information_schema.tables WHERE table_name = 'contracts'"
        )
        == 1
    )
    _ = text  # keep the import used by sibling tests
