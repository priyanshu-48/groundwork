"""query_contracts hands out real citations for one-or-two-vendor lookups (ADR 0017)."""

import json
import re
import uuid
from pathlib import Path
from typing import Any

import pytest

from app.agent.llm import FakeLLM, call, say
from app.agent.loop import run_agent
from app.agent.tools import AgentContext, execute
from app.models.document import DocKind
from app.repositories import chunks as chunks_repo
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import ingest_corpus, make_pdf, new_org, seed
from tests.integration.test_contracts import add_contract, contract_text

FIELDS = {
    "payment_terms",
    "late_fee",
    "termination_notice",
    "auto_renewal",
    "liability_cap",
    "governing_law",
}


def ctx(deps: Deps, org: uuid.UUID) -> AgentContext:
    return AgentContext(org, deps.maker, deps.embedder, deps.settings)


async def lookup(c: AgentContext, **args: Any) -> list[dict[str, Any]]:
    out = await execute(c, "query_contracts", args)
    assert not out.is_error, out.text
    return json.loads(out.text)["rows"]  # type: ignore[no-any-return]


async def ingest_one(deps: Deps, org: uuid.UUID, vendor: str, name: str) -> None:
    await seed(deps, org, make_pdf([contract_text(vendor, 45)]), "contract", name)
    while await process_one(deps, "w"):
        pass


async def test_one_vendor_lookup_comes_with_a_source_for_every_fact(deps: Deps) -> None:
    org = await new_org(deps)
    await ingest_one(deps, org, "Acme Labs", "acme.pdf")
    c = ctx(deps, org)
    (row,) = await lookup(c, vendor="acme")
    assert set(row["sources"]) == FIELDS
    # a one-page contract: every fact is on the same chunk, so one ref is reused, not six
    assert len(set(row["sources"].values())) == 1
    ref = row["sources"]["payment_terms"]
    assert c.refs[ref].filename == "acme.pdf" and c.refs[ref].page == 1
    assert "Net 45" in c.refs[ref].content


async def test_wide_queries_and_missing_chunks_return_no_sources(deps: Deps) -> None:
    org = await new_org(deps)
    for i, vendor in enumerate(["Acme Labs", "Globex Cloud", "Initech Print", "Hooli Media"]):
        await ingest_one(deps, org, vendor, f"c{i}.pdf")
    c = ctx(deps, org)
    assert all("sources" not in r for r in await lookup(c))  # 4 rows: a list, not a lookup
    assert len(c.refs) == 0
    two = await lookup(c, governing_law="delaware")  # still more than 3 matches
    assert all("sources" not in r for r in two)
    # a structured row whose document has no chunks (no text to cite) simply has no sources
    bare = await new_org(deps)
    await add_contract(deps, bare, "Bare Co", 30)
    (row,) = await lookup(ctx(deps, bare), vendor="bare")
    assert "sources" not in row


async def test_sources_never_cross_organisations(deps: Deps) -> None:
    mine, other = await new_org(deps), await new_org(deps)
    await ingest_one(deps, mine, "Acme Labs", "acme.pdf")
    c = ctx(deps, other)
    assert await lookup(c, vendor="acme") == []
    assert len(c.refs) == 0


async def test_keyword_search_can_be_limited_to_one_document(deps: Deps) -> None:
    org = await new_org(deps)
    await ingest_one(deps, org, "Acme Labs", "a.pdf")
    await ingest_one(deps, org, "Globex Cloud", "b.pdf")
    async with deps.maker() as s:
        both = await chunks_repo.keyword_search(s, org, "payment terms", DocKind.contract, 10)
        only = await chunks_repo.keyword_search(
            s, org, "payment terms", DocKind.contract, 10, document_id=both[0].document_id
        )
    assert {h.filename for h in both} == {"a.pdf", "b.pdf"}
    assert {h.document_id for h in only} == {both[0].document_id}


async def test_a_one_step_structured_answer_is_now_cited(deps: Deps) -> None:
    org = await new_org(deps)
    await ingest_one(deps, org, "Acme Labs", "acme.pdf")

    def answer(messages: Any) -> Any:
        ref = re.search(r'"payment_terms": "(C\d+)"', messages[-1].tool_results[0].text)
        assert ref
        return say(f"Net 45 [{ref.group(1)}]")

    events = [
        e
        async for e in run_agent(
            ctx(deps, org),
            FakeLLM([call("query_contracts", vendor="acme"), answer]),
            "Payment terms in the Acme contract?",
        )
    ]
    done = events[-1].data
    assert done["status"] == "ok" and [s["tool"] for s in done["steps"]] == ["query_contracts"]
    (cite,) = done["citations"]
    assert cite["filename"] == "acme.pdf" and cite["page"] == 1 and "Net 45" in cite["snippet"]


@pytest.mark.parametrize("field", sorted(FIELDS))
async def test_the_cited_page_is_the_page_that_states_the_fact(
    deps: Deps, small: tuple[dict, Path], field: str
) -> None:
    """Quality pin on the generated contracts (facts live on different pages): the ref handed
    out for each field must be the ground-truth page. The old 'cite page 1' shortcut scored 40%."""
    gt, out = small
    org = await new_org(deps)
    await ingest_corpus(deps, org, {"vendors": gt["vendors"], "invoices": []}, out)
    c = ctx(deps, org)
    wrong = []
    for v in gt["vendors"]:
        (row,) = await lookup(c, vendor=v["name"])
        want = v["contract"]["facts"][field]["page"]
        got = c.refs[row["sources"][field]].page
        if got != want:
            wrong.append((v["name"], want, got))
    assert not wrong, wrong
