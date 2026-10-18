"""Evidence: the rows behind a computed answer travel beside the tool result (ADR 0018)."""

import json
import uuid
from decimal import Decimal
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.agent.llm import FakeLLM, call, say
from app.agent.loop import run_agent
from app.agent.tools import AgentContext, ToolOutput, execute
from app.worker.deps import Deps
from app.worker.runner import process_one
from tests.helpers import add_invoice_row, invoice_text, make_pdf, new_org, seed
from tests.integration.test_chat_api import chat, new_conv, set_llm, signup
from tests.integration.test_contracts import add_contract


def ctx_for(deps: Deps, org: uuid.UUID, **settings: Any) -> AgentContext:
    s = deps.settings.model_copy(update=settings) if settings else deps.settings
    return AgentContext(org, deps.maker, deps.embedder, s)


async def run_tool(deps: Deps, org: uuid.UUID, tool: str, **args: Any) -> ToolOutput:
    out = await execute(ctx_for(deps, org), tool, args)
    assert not out.is_error, out.text
    return out


@pytest.fixture
async def org(deps: Deps) -> uuid.UUID:
    o = await new_org(deps)
    await add_invoice_row(deps, o, "Acme Corp", "A-1", "2025-03-01", "100.10")
    await add_invoice_row(deps, o, "Acme Corp", "A-2", "2025-03-31", "200.20")
    await add_invoice_row(deps, o, "Acme Corp", "A-3", "2025-04-01", "50.00")
    await add_invoice_row(deps, o, "Globex", "G-1", "2025-03-15", "70.00", currency="EUR")
    await add_invoice_row(deps, o, "Globex", "G-2", "2025-03-16", "999.99", review=True)  # flagged
    return o


def totals(evidence: dict[str, Any]) -> dict[str, Decimal]:
    return {c: Decimal(v) for c, v in evidence["totals"].items()}


async def test_a_sum_comes_with_exactly_the_invoices_that_were_summed(
    deps: Deps, org: uuid.UUID
) -> None:
    out = await run_tool(
        deps, org, "query_invoices", aggregate="sum", vendor="acme",
        date_from="2025-03-01", date_to="2025-03-31",
    )  # fmt: skip
    ev = out.evidence
    assert ev is not None and ev["kind"] == "invoices"
    assert [r["invoice_number"] for r in ev["rows"]] == ["A-1", "A-2"]  # A-3 is in April
    assert totals(ev) == {"USD": Decimal("300.30")}
    answer = json.loads(out.text)["rows"][0]
    assert Decimal(answer["total"]) == totals(ev)["USD"]  # the figure the model sees = the evidence
    assert ev["count"] == 2 and ev["truncated"] is False
    row = ev["rows"][0]
    assert row["vendor"] == "Acme Corp" and row["total"] == "100.10" and row["currency"] == "USD"
    assert row["issue_date"] == "2025-03-01"


async def test_every_aggregate_shape_has_matching_evidence(deps: Deps, org: uuid.UUID) -> None:
    grouped = await run_tool(deps, org, "query_invoices", aggregate="sum", group_by_vendor=True)
    assert grouped.evidence is not None
    assert {r["vendor"] for r in grouped.evidence["rows"]} == {"Acme Corp", "Globex"}
    assert totals(grouped.evidence) == {"USD": Decimal("350.30"), "EUR": Decimal("70.00")}
    counted = await run_tool(deps, org, "query_invoices", aggregate="count")
    assert counted.evidence is not None and counted.evidence["count"] == 4  # the flagged one is out
    listed = await run_tool(deps, org, "query_invoices", aggregate="list", vendor="globex")
    assert listed.evidence is not None
    assert [r["invoice_number"] for r in listed.evidence["rows"]] == ["G-1"]


async def test_flagged_invoices_are_in_neither_the_answer_nor_the_evidence(
    deps: Deps, org: uuid.UUID
) -> None:
    out = await run_tool(deps, org, "query_invoices", aggregate="sum", vendor="globex")
    assert out.evidence is not None
    assert "G-2" not in json.dumps(out.evidence) and totals(out.evidence) == {"EUR": Decimal("70")}


async def test_the_payment_terms_filter_applies_to_the_evidence_too(deps: Deps) -> None:
    o = await new_org(deps)
    await add_contract(deps, o, "Acme Labs", 30)
    await add_contract(deps, o, "Globex Cloud", 45)
    await add_invoice_row(deps, o, "Acme Labs", "A-1", "2025-03-05", "100.00")
    await add_invoice_row(deps, o, "Globex Cloud", "G-1", "2025-03-06", "400.00")
    out = await run_tool(
        deps, o, "query_invoices", aggregate="sum", payment_terms_days=45, group_by_vendor=True
    )
    assert out.evidence is not None
    assert [r["vendor"] for r in out.evidence["rows"]] == ["Globex Cloud"]
    assert totals(out.evidence) == {"USD": Decimal("400.00")}


async def test_a_long_list_is_cut_but_the_totals_still_cover_everything(deps: Deps) -> None:
    o = await new_org(deps)
    for i in range(5):
        await add_invoice_row(deps, o, "Acme Corp", f"A-{i}", f"2025-03-0{i + 1}", "10.00")
    out = await execute(
        ctx_for(deps, o, evidence_max_rows=2), "query_invoices", {"aggregate": "sum"}
    )
    ev = out.evidence
    assert ev is not None and len(ev["rows"]) == 2
    assert (ev["count"], ev["truncated"]) == (5, True)
    assert totals(ev) == {
        "USD": Decimal("50.00")
    }  # computed in SQL over all five, not the two shown


async def test_rows_carry_their_source_file_and_page(deps: Deps) -> None:
    o = await new_org(deps)
    pdf = make_pdf([invoice_text(vendor="Acme Corp", number="V1", total="110.00")])
    await seed(deps, o, pdf, "invoice", "inv_v1.pdf")
    while await process_one(deps, "w"):
        pass
    out = await run_tool(deps, o, "query_invoices", aggregate="sum")
    assert out.evidence is not None
    (row,) = out.evidence["rows"]
    assert row["invoice_number"] == "V1" and row["total"] == "110.00"
    assert row["filename"] == "inv_v1.pdf" and row["page"] == 1


async def test_vendor_wildcards_stay_literal_and_other_orgs_get_nothing(
    deps: Deps, org: uuid.UUID
) -> None:
    for evil in ["%", "_", "x'; DROP TABLE invoices; --"]:
        out = await run_tool(deps, org, "query_invoices", aggregate="sum", vendor=evil)
        assert out.evidence is not None and out.evidence["rows"] == []
    stranger = await new_org(deps)
    out = await run_tool(deps, stranger, "query_invoices", aggregate="sum")
    assert out.evidence is not None and out.evidence["rows"] == [] and out.evidence["count"] == 0


async def test_the_model_never_sees_the_evidence(deps: Deps, org: uuid.UUID) -> None:
    out = await run_tool(deps, org, "query_invoices", aggregate="sum")
    assert out.evidence is not None
    assert "evidence" not in out.text and "A-1" not in out.text  # no extra tokens, same behaviour


async def test_contract_lists_come_with_their_rows(deps: Deps) -> None:
    o = await new_org(deps)
    await add_contract(deps, o, "Acme Labs", 30)
    await add_contract(deps, o, "Globex Cloud", 45)
    await add_contract(deps, o, "Initech Print", 30)
    out = await run_tool(deps, o, "query_contracts", payment_terms_days=30)
    assert out.evidence is not None and out.evidence["kind"] == "contracts"
    assert [r["vendor"] for r in out.evidence["rows"]] == ["Acme Labs", "Initech Print"]
    assert out.evidence["rows"][0]["payment_terms_days"] == 30
    assert "evidence" not in out.text


async def test_tools_without_a_computed_answer_have_no_evidence(deps: Deps, org: uuid.UUID) -> None:
    out = await execute(ctx_for(deps, org), "search_documents", {"query": "anything"})
    assert out.evidence is None


async def test_the_step_event_and_stored_step_carry_the_evidence(
    deps: Deps, org: uuid.UUID
) -> None:
    llm = FakeLLM([call("query_invoices", aggregate="sum", vendor="acme"), say("USD 350.30")])
    events = [e async for e in run_agent(ctx_for(deps, org), llm, "How much did Acme bill?")]
    ok_steps = [e.data for e in events if e.type == "step" and e.data["status"] == "ok"]
    assert ok_steps[0]["evidence"]["totals"] == {"USD": "350.30"}
    running = [e.data for e in events if e.type == "step" and e.data["status"] == "running"]
    assert "evidence" not in running[0]
    done = events[-1].data
    assert done["steps"][0]["evidence"]["count"] == 3


def test_history_returns_the_evidence_of_a_past_answer(client: TestClient) -> None:
    h, org = signup(client)
    deps: Deps = client.app.state.agent_deps  # type: ignore[attr-defined]
    client.portal.call(
        add_invoice_row, deps, uuid.UUID(org), "Acme Corp", "A-1", "2025-03-01", "100.10"
    )  # type: ignore[union-attr]
    conv = new_conv(client, h)
    set_llm(client, FakeLLM([call("query_invoices", aggregate="sum"), say("USD 100.10")]))
    assert chat(client, h, conv).status_code == 200
    msgs = client.get(f"/conversations/{conv}/messages", headers=h).json()
    steps = msgs[-1]["steps"]
    assert steps[0]["tool"] == "query_invoices"
    assert steps[0]["evidence"]["totals"] == {"USD": "100.10"}
    assert steps[0]["evidence"]["rows"][0]["invoice_number"] == "A-1"
