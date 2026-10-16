import json
import re
from collections import Counter

import pytest
from evals.build_questions import BANNED, build_retrieval_questions
from evals.generate_corpus import build_ground_truth


@pytest.fixture(scope="module")
def gt() -> dict:
    return build_ground_truth(seed=42, n_vendors=25, n_invoices=300)


@pytest.fixture(scope="module")
def qs(gt: dict) -> list[dict]:
    return build_retrieval_questions(gt, seed=42)


def test_counts_ids_and_determinism(gt: dict, qs: list[dict]) -> None:
    assert Counter(q["type"] for q in qs) == {
        "retrieval_invoice_id": 20,
        "retrieval_paraphrase": 24,
        "retrieval_invoice_fields": 16,
    }
    assert len({q["id"] for q in qs}) == 60
    assert json.dumps(build_retrieval_questions(gt, seed=42)) == json.dumps(qs)


def test_gold_documents_and_pages_exist(gt: dict, qs: list[dict]) -> None:
    pages = {v["contract"]["filename"]: v["contract"]["pages"] for v in gt["vendors"]}
    pages |= {i["filename"]: 1 for i in gt["invoices"]}
    for q in qs:
        assert q["gold"]["document"] in pages
        assert 1 <= q["gold"]["page"] <= pages[q["gold"]["document"]]


def test_exact_id_questions_contain_the_real_invoice_number(gt: dict, qs: list[dict]) -> None:
    by_file = {i["filename"]: i for i in gt["invoices"]}
    for q in (q for q in qs if q["type"] == "retrieval_invoice_id"):
        assert by_file[q["gold"]["document"]]["invoice_number"] in q["question"]


def test_field_questions_carry_vendor_date_and_total(gt: dict, qs: list[dict]) -> None:
    by_file = {i["filename"]: i for i in gt["invoices"]}
    for q in (q for q in qs if q["type"] == "retrieval_invoice_fields"):
        inv = by_file[q["gold"]["document"]]
        assert inv["vendor"] in q["question"] and inv["issue_date"] in q["question"]
        assert f"{float(inv['total']):,.2f}" in q["question"]
        assert inv["invoice_number"] not in q["question"]  # otherwise it is the exact-ID task


def test_paraphrases_share_no_key_terms_with_the_clause(gt: dict, qs: list[dict]) -> None:
    by_file = {v["contract"]["filename"]: v for v in gt["vendors"]}
    paraphrases = [q for q in qs if q["type"] == "retrieval_paraphrase"]
    assert {q["fact"] for q in paraphrases} == set(BANNED)
    for q in paraphrases:
        words = set(re.findall(r"[a-z]+", q["question"].lower()))
        for banned in BANNED[q["fact"]]:
            assert not any(w.startswith(banned) for w in words), (q["question"], banned)
        v = by_file[q["gold"]["document"]]
        assert v["name"] in q["question"]
        assert q["gold"]["page"] == v["contract"]["facts"][q["fact"]]["page"]
