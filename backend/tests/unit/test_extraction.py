from datetime import date
from decimal import Decimal

import pytest

from app.services.extraction import FakeInvoiceExtractor, InvoiceFields, review_reason
from tests.helpers import invoice_text


def _good(**kw: object) -> InvoiceFields:
    base: dict[str, object] = dict(
        vendor="Acme",
        invoice_number="INV-1",
        issue_date=date(2025, 3, 5),
        due_date=date(2025, 4, 19),
        currency="USD",
        subtotal=Decimal("100.00"),
        tax=Decimal("10.00"),
        total=Decimal("110.00"),
    )
    base.update(kw)
    return InvoiceFields(**base)  # type: ignore[arg-type]


def test_consistent_invoice_is_clean() -> None:
    assert review_reason(_good()) is None


def test_totals_that_do_not_add_up_are_flagged() -> None:
    assert "subtotal" in (review_reason(_good(total=Decimal("999.00"))) or "")


def test_missing_tax_counts_as_zero() -> None:
    assert review_reason(_good(tax=None, total=Decimal("100.00"))) is None


def test_decimal_arithmetic_has_no_float_drift() -> None:
    f = _good(subtotal=Decimal("0.10"), tax=Decimal("0.20"), total=Decimal("0.30"))
    assert review_reason(f) is None


def test_missing_required_fields_are_flagged() -> None:
    assert review_reason(_good(vendor=None)) is not None
    assert review_reason(_good(invoice_number=None)) is not None
    assert review_reason(_good(total=None)) is not None


def test_bad_currency_is_flagged() -> None:
    assert review_reason(_good(currency="US")) is not None


async def test_fake_extractor_reads_labelled_lines() -> None:
    f = await FakeInvoiceExtractor().extract(invoice_text(vendor="Globex", total="110.00"))
    assert (f.vendor, f.invoice_number, f.total) == ("Globex", "INV-1", Decimal("110.00"))
    assert f.issue_date == date(2025, 3, 5)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("1,155.05", "1155.05"),
        ("USD 1,155.05", "1155.05"),
        ("$ 76 049.20", "76049.20"),
        ("1.155,05", "1155.05"),  # decimal comma
        ("12,50", "12.50"),
        ("1,155", "1155"),  # thousands separator, not a decimal comma
        (13057.07, "13057.07"),
        (100, "100"),
        ("4936.83", "4936.83"),
        ("-12.30", "-12.30"),
    ],
)
def test_money_parsing_tolerates_formats_models_produce(raw: object, expected: str) -> None:
    from app.services.extraction import _money

    assert _money(raw) == Decimal(expected)  # type: ignore[arg-type]


@pytest.mark.parametrize("raw", [None, "", "n/a", "abc", "--", "."])
def test_unparseable_money_is_none_not_a_guess(raw: object) -> None:
    from app.services.extraction import _money

    assert _money(raw) is None  # type: ignore[arg-type]
