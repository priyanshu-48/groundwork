import json
import uuid
from typing import Any

import pytest

from app.agent.tools import AgentContext, execute
from app.worker.deps import Deps
from tests.helpers import add_invoice_row, new_org


def ctx_for(deps: Deps, org: uuid.UUID) -> AgentContext:
    return AgentContext(org, deps.maker, deps.embedder, deps.settings)


async def q(deps: Deps, org: uuid.UUID, **args: Any) -> dict[str, Any]:
    out = await execute(ctx_for(deps, org), "query_invoices", args)
    assert not out.is_error, out.text
    return json.loads(out.text)  # type: ignore[no-any-return]


@pytest.fixture
async def org(deps: Deps) -> uuid.UUID:
    o = await new_org(deps)
    await add_invoice_row(deps, o, "Acme Corp", "A-1", "2025-03-01", "100.10")
    await add_invoice_row(deps, o, "Acme Corp", "A-2", "2025-03-31", "200.20")
    await add_invoice_row(deps, o, "Acme Corp", "A-3", "2025-04-01", "50.00")
    await add_invoice_row(deps, o, "Globex", "G-1", "2025-03-15", "70.00", currency="EUR")
    await add_invoice_row(deps, o, "Globex", "G-2", "2025-03-16", "999.99", review=True)
    return o


async def test_sum_is_exact_decimal_and_grouped_by_currency(deps: Deps, org: uuid.UUID) -> None:
    r = await q(deps, org, aggregate="sum", date_from="2025-03-01", date_to="2025-03-31")
    by_cur = {row["currency"]: row for row in r["rows"]}
    assert by_cur["USD"]["total"] == "300.30" and by_cur["USD"]["invoice_count"] == 2
    assert by_cur["EUR"]["total"] == "70.00"  # never added to USD


async def test_flagged_invoices_never_count(deps: Deps, org: uuid.UUID) -> None:
    r = await q(deps, org, aggregate="count", vendor="Globex")
    assert r["rows"] == [{"invoice_count": 1}]  # G-2 is needs_review


async def test_group_by_vendor_and_vendor_list(deps: Deps, org: uuid.UUID) -> None:
    r = await q(deps, org, aggregate="sum", vendors=["Acme", "Globex"], group_by_vendor=True)
    totals = {(x["vendor"], x["currency"]): x["total"] for x in r["rows"]}
    assert totals == {("Acme Corp", "USD"): "350.30", ("Globex", "EUR"): "70.00"}
    assert r["rows"][0]["vendor"] == "Acme Corp"  # biggest first


async def test_date_range_is_inclusive_on_both_ends(deps: Deps, org: uuid.UUID) -> None:
    r = await q(
        deps, org, aggregate="list", vendor="Acme", date_from="2025-03-31", date_to="2025-04-01"
    )
    assert [x["invoice_number"] for x in r["rows"]] == ["A-2", "A-3"]


async def test_list_is_ordered_and_limited(deps: Deps, org: uuid.UUID) -> None:
    r = await q(deps, org, aggregate="list", vendor="acme", limit=2)  # case-insensitive
    assert [x["invoice_number"] for x in r["rows"]] == ["A-1", "A-2"]


async def test_like_wildcards_in_the_vendor_are_literal(deps: Deps, org: uuid.UUID) -> None:
    for evil in ["%", "_", "A%", "Acme_Corp", "\\"]:
        r = await q(deps, org, aggregate="count", vendor=evil)
        assert r["rows"] == [{"invoice_count": 0}], evil


async def test_sql_injection_text_is_just_a_vendor_name(deps: Deps, org: uuid.UUID) -> None:
    r = await q(deps, org, aggregate="count", vendor="x'; DROP TABLE invoices; --")
    assert r["rows"] == [{"invoice_count": 0}]
    assert (await q(deps, org, aggregate="count"))["rows"] == [{"invoice_count": 4}]  # still there


async def test_another_org_sees_none_of_it(deps: Deps, org: uuid.UUID) -> None:
    stranger = await new_org(deps)
    assert (await q(deps, stranger, aggregate="count"))["rows"] == [{"invoice_count": 0}]
    assert (await q(deps, stranger, aggregate="list"))["rows"] == []


@pytest.mark.parametrize(
    "args",
    [
        {"aggregate": "sum", "vendor": "a", "vendors": ["b"]},
        {"aggregate": "sum", "date_from": "2025-05-01", "date_to": "2025-01-01"},
        {"aggregate": "list", "group_by_vendor": True},
        {"aggregate": "avg"},
        {"aggregate": "sum", "limit": 51},
        {"aggregate": "sum", "vendors": [f"v{i}" for i in range(11)]},
        {"aggregate": "sum", "org_id": str(uuid.uuid4())},
        {"aggregate": "sum", "sql": "select 1"},
    ],
)
async def test_bad_arguments_come_back_as_errors_the_model_can_fix(
    deps: Deps, org: uuid.UUID, args: dict[str, Any]
) -> None:
    out = await execute(ctx_for(deps, org), "query_invoices", args)
    assert out.is_error and out.text.startswith("Error: invalid arguments")
