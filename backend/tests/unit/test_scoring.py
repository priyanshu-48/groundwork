import pytest
from evals.scoring import citation_counts, score_answer, score_contract

VENDORS = ["Acme Labs", "Globex Cloud", "Initech Print"]


@pytest.mark.parametrize(
    ("fact", "gold", "answer", "ok"),
    [
        (
            "payment_terms",
            "net-45",
            "Payment is due within forty-five (45) days (Net 45). [C1]",
            True,
        ),
        ("payment_terms", "net-45", "The terms are net-30.", False),
        ("payment_terms", "net-45", "Net 30 for services, Net 45 for goods.", False),  # hedged
        ("late_fee", "1.5%", "A late fee of 1.5% per month applies [C2].", True),
        ("late_fee", "1.5%", "A late fee of 1.0% per month applies.", False),
        ("late_fee", "1.5%", "It is 1.5 percent monthly.", True),
        ("termination_notice", "60 days", "Either party must give sixty (60) days' notice.", True),
        ("termination_notice", "60 days", "90 days written notice.", False),
        ("auto_renewal", "yes", "Yes, it renews automatically each year.", True),
        ("auto_renewal", "no", "No, the agreement does not renew automatically.", True),
        ("auto_renewal", "no", "It renews automatically.", False),
        ("auto_renewal", "yes", "It does not renew automatically.", False),
        ("liability_cap", "USD 250,000", "Liability is capped at USD 250,000 [C1].", True),
        ("liability_cap", "USD 250,000", "The cap is 1,000,000.", False),
        ("governing_law", "State of Delaware", "Delaware law governs.", True),
        ("governing_law", "State of Delaware", "The laws of the State of New York.", False),
        (
            "governing_law",
            "England and Wales",
            "It is governed by the law of England and Wales.",
            True,
        ),
    ],
)
def test_contract_answers(fact: str, gold: str, answer: str, ok: bool) -> None:
    assert score_contract(fact, gold, answer) is ok


def q(**kw: object) -> dict:
    return {"type": "invoice_aggregate", **kw}


def test_sum_matches_the_exact_decimal_and_ignores_dates_and_invoice_numbers() -> None:
    question = q(answer="12345.60", answer_type="decimal")
    assert score_answer(
        question, "Between 2025-04-01 and 2025-06-30 you were billed USD 12,345.60.", VENDORS
    )
    assert not score_answer(question, "You were billed USD 12,345.00.", VENDORS)
    assert not score_answer(question, "I could not find that.", VENDORS)


def test_count_is_not_fooled_by_dates_or_invoice_numbers() -> None:
    question = q(answer=4, answer_type="int")
    assert score_answer(
        question, "There were 4 invoices between 2025-04-01 and 2025-06-30.", VENDORS
    )
    assert not score_answer(
        question, "There were 5 invoices (V04-2025-0004 and others) in 2025-04-01.", VENDORS
    )


def test_list_needs_exactly_the_right_invoices() -> None:
    question = q(answer=["V01-2025-0001", "V01-2025-0002"], answer_type="list")
    assert score_answer(question, "V01-2025-0001 and V01-2025-0002", VENDORS)
    assert not score_answer(question, "V01-2025-0001 only", VENDORS)
    assert not score_answer(question, "V01-2025-0001, V01-2025-0002, V01-2025-0003", VENDORS)


def test_multi_hop_vendor_must_be_named_alone() -> None:
    question = {"type": "multi_hop", "answer": "Acme Labs", "answer_type": "text"}
    assert score_answer(question, "Acme Labs billed the most [C1].", VENDORS)
    assert not score_answer(question, "Globex Cloud billed the most.", VENDORS)
    assert not score_answer(question, "Acme Labs and Globex Cloud both billed a lot.", VENDORS)


def test_multi_hop_total_is_a_decimal_match() -> None:
    question = {"type": "multi_hop", "answer": "5000.10", "answer_type": "decimal"}
    assert score_answer(question, "USD 5,000.10 in total.", VENDORS)


GT = {
    "invoices": [
        {"filename": "i1.pdf", "vendor": "Acme Labs", "issue_date": "2025-04-10"},
        {"filename": "i2.pdf", "vendor": "Acme Labs", "issue_date": "2025-09-10"},
        {"filename": "i3.pdf", "vendor": "Globex Cloud", "issue_date": "2025-04-11"},
    ]
}


def test_citation_precision_for_contract_lookups_needs_document_and_page() -> None:
    question = {"type": "contract_lookup", "gold": {"document": "c.pdf", "page": 2}}
    cites = [
        {"filename": "c.pdf", "page": 2},
        {"filename": "c.pdf", "page": 3},
        {"filename": "other.pdf", "page": 2},
    ]
    assert citation_counts(question, cites, GT) == (1, 3)


def test_citation_precision_for_aggregates_uses_vendor_and_date_range() -> None:
    question = q(vendor="Acme Labs", date_from="2025-04-01", date_to="2025-06-30")
    cites = [
        {"filename": "i1.pdf", "page": 1},
        {"filename": "i2.pdf", "page": 1},
        {"filename": "i3.pdf", "page": 1},
    ]
    assert citation_counts(question, cites, GT) == (1, 3)


def test_precision_is_undefined_for_multi_hop() -> None:
    assert citation_counts({"type": "multi_hop"}, [{"filename": "x", "page": 1}], GT) is None
