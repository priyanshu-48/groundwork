import json
from collections import Counter
from datetime import date
from decimal import Decimal

import pytest
from evals.build_questions import build_questions
from evals.generate_corpus import build_ground_truth


@pytest.fixture(scope="module")
def gt() -> dict:
    return build_ground_truth(seed=42, n_vendors=25, n_invoices=300)


@pytest.fixture(scope="module")
def questions(gt: dict) -> list[dict]:
    return build_questions(gt, seed=42)


def test_counts_and_unique_ids(questions: list[dict]) -> None:
    assert Counter(q["type"] for q in questions) == {
        "contract_lookup": 35,
        "invoice_aggregate": 35,
        "multi_hop": 20,
    }
    assert len({q["id"] for q in questions}) == 90


def test_deterministic(gt: dict, questions: list[dict]) -> None:
    assert json.dumps(build_questions(gt, seed=42)) == json.dumps(questions)


def test_contract_lookups_point_at_a_real_page_with_the_right_fact(
    gt: dict, questions: list[dict]
) -> None:
    by_file = {v["contract"]["filename"]: v for v in gt["vendors"]}
    lookups = [q for q in questions if q["type"] == "contract_lookup"]
    assert len({q["fact"] for q in lookups}) == 6  # every fact type is exercised
    for q in lookups:
        v = by_file[q["gold"]["document"]]
        fact = v["contract"]["facts"][q["fact"]]
        assert q["gold"]["page"] == fact["page"] <= v["contract"]["pages"]
        assert v["name"] in q["question"]
        assert q["answer"] == fact["value"]


def _inv_in_range(gt: dict, vendor: str, lo: str, hi: str) -> list[dict]:
    return [
        i
        for i in gt["invoices"]
        if i["vendor"] == vendor
        and date.fromisoformat(lo) <= date.fromisoformat(i["issue_date"]) <= date.fromisoformat(hi)
    ]


def test_aggregate_answers_match_independent_recomputation(gt: dict, questions: list[dict]) -> None:
    aggs = [q for q in questions if q["type"] == "invoice_aggregate"]
    assert {q["aggregate"] for q in aggs} == {"sum", "count", "list"}
    for q in aggs:
        rows = _inv_in_range(gt, q["vendor"], q["date_from"], q["date_to"])
        assert rows, "questions must have at least one matching invoice"
        if q["aggregate"] == "sum":
            assert Decimal(q["answer"]) == sum(Decimal(r["total"]) for r in rows)
        elif q["aggregate"] == "count":
            assert q["answer"] == len(rows)
        else:
            assert q["answer"] == sorted(r["invoice_number"] for r in rows)


def test_multi_hop_answers_and_single_currency(gt: dict, questions: list[dict]) -> None:
    terms_of = {v["name"]: v["contract"]["facts"]["payment_terms"]["value"] for v in gt["vendors"]}
    cur_of = {v["name"]: v["currency"] for v in gt["vendors"]}
    hops = [q for q in questions if q["type"] == "multi_hop"]
    assert len(hops) == 20
    for q in hops:
        totals: dict[str, Decimal] = {}
        for i in gt["invoices"]:
            if terms_of[i["vendor"]] == q["terms"] and i["issue_date"].startswith(q["month"]):
                totals[i["vendor"]] = totals.get(i["vendor"], Decimal(0)) + Decimal(i["total"])
        assert totals and {cur_of[v] for v in totals} == {"USD"}
        if q["answer_type"] == "text":
            best = max(totals.values())
            assert [v for v, t in totals.items() if t == best] == [q["answer"]]  # unique winner
        else:
            assert Decimal(q["answer"]) == sum(totals.values())
