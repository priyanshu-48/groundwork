import json
from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from evals.generate_corpus import build_ground_truth, render_corpus
from google.genai import errors

from app.services.contract_extraction import (
    ContractFields,
    fake_extract,
    parse_bool,
    parse_int,
    parse_percent,
    review_contract,
)
from app.services.extraction import GeminiInvoiceExtractor
from app.services.gemini import ModelChain
from app.services.parsing import extract_pages


def good(**kw: Any) -> ContractFields:
    base: dict[str, Any] = dict(
        vendor="Acme",
        payment_terms_days=45,
        late_fee_percent=Decimal("1.5"),
        termination_notice_days=60,
        auto_renewal=True,
        liability_cap_amount=Decimal("250000"),
        liability_cap_currency="usd",
        governing_law="State of Delaware",
    )
    base.update(kw)
    return ContractFields(**base)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("net-45", 45), ("Net 45", 45), ("45 days", 45), (45, 45), (45.0, 45), ("forty-five", None),
     (45.5, None), (None, None), (True, None), ("", None)],
)  # fmt: skip
def test_parse_int(raw: Any, expected: int | None) -> None:
    assert parse_int(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("1.5%", "1.5"), ("1.5 percent per month", "1.5"), (1.5, "1.5"), ("1,5 %", "1.5"),
     ("two percent", None), (None, None)],
)  # fmt: skip
def test_parse_percent(raw: Any, expected: str | None) -> None:
    assert parse_percent(raw) == (Decimal(expected) if expected else None)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [(True, True), (False, False), ("yes", True), ("Yes", True), ("false", False), ("No", False),
     ("renews automatically each year", True), ("does not renew", False), ("maybe", None),
     (None, None)],
)  # fmt: skip
def test_parse_bool(raw: Any, expected: bool | None) -> None:
    assert parse_bool(raw) is expected


def test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased() -> None:
    f = good()
    assert review_contract(f) is None and f.liability_cap_currency == "USD"


@pytest.mark.parametrize(
    ("kw", "text"),
    [
        ({"vendor": None}, "missing fields: vendor"),
        ({"auto_renewal": None}, "auto_renewal"),
        ({"payment_terms_days": 0}, "implausible payment terms"),
        ({"payment_terms_days": 4000}, "implausible payment terms"),
        ({"termination_notice_days": 999}, "implausible termination notice"),
        ({"late_fee_percent": Decimal("150")}, "implausible late fee"),
        ({"liability_cap_amount": Decimal("0")}, "implausible liability cap"),
        ({"liability_cap_currency": "US"}, "invalid currency"),
    ],
)
def test_review_flags_missing_and_implausible_values(kw: dict[str, Any], text: str) -> None:
    assert text in (review_contract(good(**kw)) or "")


def test_fake_extractor_reads_every_fact_of_the_generated_corpus(tmp_path: Path) -> None:
    gt = build_ground_truth(seed=42, n_vendors=6, n_invoices=6)
    render_corpus(gt, tmp_path, seed=42)
    for v in gt["vendors"]:
        pdf = (tmp_path / "contracts" / v["contract"]["filename"]).read_bytes()
        f = fake_extract("\n".join(extract_pages(pdf, 50)))
        facts = v["contract"]["facts"]
        cur, amount = facts["liability_cap"]["value"].split()
        assert f.vendor == v["name"]
        assert f.payment_terms_days == int(facts["payment_terms"]["value"].split("-")[1])
        assert f.late_fee_percent == Decimal(facts["late_fee"]["value"].rstrip("%"))
        assert f.termination_notice_days == int(facts["termination_notice"]["value"].split()[0])
        assert f.auto_renewal is (facts["auto_renewal"]["value"] == "yes")
        assert (f.liability_cap_currency, f.liability_cap_amount) == (
            cur,
            Decimal(amount.replace(",", "")),
        )
        assert f.governing_law == facts["governing_law"]["value"]
        assert review_contract(f) is None


def contract(index: int, vendor: str, terms: Any = 45) -> dict[str, Any]:
    return {
        "index": index, "vendor": vendor, "payment_terms_days": terms, "late_fee_percent": "1.5%",
        "termination_notice_days": 60, "auto_renewal": "yes", "liability_cap_amount": "USD 250,000",
        "liability_cap_currency": "USD", "governing_law": "State of Delaware",
    }  # fmt: skip


class Models:
    def __init__(self, body: Any, fail: tuple[str, ...] = ()) -> None:
        self.body, self.fail, self.calls = body, fail, []

    def generate_content(self, *, model: str, contents: str, config: Any) -> Any:
        self.calls.append((model, contents))
        if model in self.fail:
            raise errors.APIError(429, {"error": {"message": "PerDay 'retryDelay': '3600s'"}})
        return SimpleNamespace(
            text=self.body if isinstance(self.body, str) else json.dumps(self.body)
        )


def extractor(body: Any, models: list[str] | None = None, fail: tuple[str, ...] = ()):  # type: ignore[no-untyped-def]
    m = Models(body, fail)
    return GeminiInvoiceExtractor(SimpleNamespace(models=m), ModelChain(models or ["m1"])), m


async def test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats() -> None:
    body = {"contracts": [contract(2, "Beta", "net-30"), contract(1, "Alpha", 45.0)]}  # shuffled
    ex, m = extractor(body)
    out = await ex.extract_contracts_many(["alpha text", "beta text"])
    assert len(m.calls) == 1
    assert [f.vendor for f in out] == ["Alpha", "Beta"]
    assert [f.payment_terms_days for f in out] == [45, 30]
    assert out[0].liability_cap_amount == Decimal("250000") and out[0].auto_renewal is True
    assert all(review_contract(f) is None for f in out)


async def test_missing_garbled_or_invalid_entries_become_flagged_empties() -> None:
    ex, _ = extractor({"contracts": [contract(1, "Alpha")]})
    out = await ex.extract_contracts_many(["a", "b"])
    assert out[0].vendor == "Alpha" and review_contract(out[1]) is not None
    ex, _ = extractor("not json at all")
    assert all(review_contract(f) is not None for f in await ex.extract_contracts_many(["a"]))


async def test_documents_are_wrapped_numbered_and_capped() -> None:
    ex, m = extractor({"contracts": []})
    await ex.extract_contracts_many(["x" * 30000, "second"])
    prompt = m.calls[0][1]
    assert "<document index=1>" in prompt and "<document index=2>" in prompt
    assert "x" * 16000 in prompt and "x" * 16001 not in prompt


async def test_contract_extraction_falls_over_to_the_next_model() -> None:
    ex, m = extractor({"contracts": [contract(1, "Alpha")]}, ["m1", "m2"], fail=("m1",))
    single = await ex.extract_contract("text")
    assert single.vendor == "Alpha" and [c[0] for c in m.calls] == ["m1", "m2"]
