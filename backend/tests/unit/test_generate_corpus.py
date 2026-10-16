import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pymupdf
import pytest
from evals.generate_corpus import build_ground_truth, render_corpus

SMALL = dict(seed=42, n_vendors=6, n_invoices=24)
FACT_KINDS = {
    "payment_terms",
    "late_fee",
    "termination_notice",
    "auto_renewal",
    "liability_cap",
    "governing_law",
}


def test_ground_truth_is_deterministic() -> None:
    a, b = build_ground_truth(**SMALL), build_ground_truth(**SMALL)
    assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    assert json.dumps(a, sort_keys=True) != json.dumps(
        build_ground_truth(seed=7, n_vendors=6, n_invoices=24), sort_keys=True
    )


def test_full_size_counts() -> None:
    gt = build_ground_truth(seed=42, n_vendors=25, n_invoices=300)
    assert len(gt["vendors"]) == 25 and len(gt["invoices"]) == 300
    assert len({v["name"] for v in gt["vendors"]}) == 25
    for v in gt["vendors"]:
        assert 3 <= v["contract"]["pages"] <= 6
        assert set(v["contract"]["facts"]) == FACT_KINDS
        assert all(
            1 <= f["page"] <= v["contract"]["pages"] for f in v["contract"]["facts"].values()
        )


def test_foreign_currency_vendors_only_get_net_15_or_60() -> None:
    gt = build_ground_truth(seed=42, n_vendors=25, n_invoices=300)
    foreign = [v for v in gt["vendors"] if v["currency"] != "USD"]
    assert len(foreign) == 5
    assert {v["contract"]["facts"]["payment_terms"]["value"] for v in foreign} <= {
        "net-15",
        "net-60",
    }


def test_invoice_math_numbers_and_due_dates() -> None:
    gt = build_ground_truth(seed=42, n_vendors=25, n_invoices=300)
    vendors = {v["id"]: v for v in gt["vendors"]}
    seen: set[tuple[int, str]] = set()
    for inv in gt["invoices"]:
        assert Decimal(inv["subtotal"]) + Decimal(inv["tax"]) == Decimal(inv["total"])
        assert sum(Decimal(line["amount"]) for line in inv["lines"]) == Decimal(inv["subtotal"])
        key = (inv["vendor_id"], inv["invoice_number"])
        assert key not in seen
        seen.add(key)
        v = vendors[inv["vendor_id"]]
        days = int(v["contract"]["facts"]["payment_terms"]["value"].split("-")[1])
        assert date.fromisoformat(inv["due_date"]) == date.fromisoformat(
            inv["issue_date"]
        ) + timedelta(days=days)
        assert inv["currency"] == v["currency"] and inv["issue_date"].startswith("2025-")
    assert {i["template"] for i in gt["invoices"]} == {0, 1, 2}
    assert any(Decimal(i["tax"]) == 0 for i in gt["invoices"])
    assert any(Decimal(i["tax"]) > 0 for i in gt["invoices"])


@pytest.fixture(scope="module")
def small_corpus(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict, Path]:
    out = tmp_path_factory.mktemp("corpus")
    gt = build_ground_truth(**SMALL)
    render_corpus(gt, out, seed=42)  # also verifies every fact is on its recorded page
    return gt, out


def test_every_fact_is_on_its_gold_page(small_corpus: tuple[dict, Path]) -> None:
    gt, out = small_corpus
    for v in gt["vendors"]:
        with pymupdf.open(out / "contracts" / v["contract"]["filename"]) as doc:
            assert doc.page_count == v["contract"]["pages"]
            for fact in v["contract"]["facts"].values():
                text = " ".join(doc[fact["page"] - 1].get_text().split())
                assert " ".join(fact["text"].split()) in text
                assert v["name"] in text  # vendor name is on every page


def test_all_files_written_and_pdfs_are_byte_identical_across_runs(
    small_corpus: tuple[dict, Path], tmp_path: Path
) -> None:
    gt, out = small_corpus
    assert len(list((out / "contracts").glob("*.pdf"))) == 6
    assert len(list((out / "invoices").glob("*.pdf"))) == 24
    render_corpus(build_ground_truth(**SMALL), tmp_path, seed=42)
    for p in (
        sorted((out / "invoices").glob("*.pdf"))[:3] + sorted((out / "contracts").glob("*.pdf"))[:2]
    ):
        assert p.read_bytes() == (tmp_path / p.parent.name / p.name).read_bytes()
