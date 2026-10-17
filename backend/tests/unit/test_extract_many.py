import json
from types import SimpleNamespace
from typing import Any

from google.genai import errors

from app.services.extraction import GeminiInvoiceExtractor, review_reason
from app.services.gemini import ModelChain


def invoice(index: int, number: str, total: str = "110.00") -> dict[str, Any]:
    return {
        "index": index,
        "vendor": "Acme",
        "invoice_number": number,
        "issue_date": "2025-03-05",
        "currency": "USD",
        "subtotal": "100.00",
        "tax": "10.00",
        "total": total,
    }


class Models:
    def __init__(self, body: Any, fail_models: tuple[str, ...] = ()) -> None:
        self.body, self.fail, self.calls = body, fail_models, []

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


async def test_one_request_serves_the_whole_batch_and_results_line_up_by_index() -> None:
    body = {"invoices": [invoice(3, "C"), invoice(1, "A"), invoice(2, "B")]}  # shuffled
    ex, m = extractor(body)
    out = await ex.extract_many(["text A", "text B", "text C"])
    assert len(m.calls) == 1
    assert [f.invoice_number for f in out] == ["A", "B", "C"]
    assert all(review_reason(f) is None for f in out)


async def test_missing_or_garbled_entries_become_flagged_empties() -> None:
    ex, _ = extractor({"invoices": [invoice(1, "A")]})
    out = await ex.extract_many(["a", "b"])
    assert out[0].invoice_number == "A" and review_reason(out[1]) is not None
    ex, _ = extractor("this is not json")
    assert all(review_reason(f) is not None for f in await ex.extract_many(["a", "b"]))


async def test_each_document_is_wrapped_numbered_and_size_capped() -> None:
    ex, m = extractor({"invoices": []})
    await ex.extract_many(["x" * 9000, "second"])
    prompt = m.calls[0][1]
    assert "<document index=1>" in prompt and "<document index=2>" in prompt
    assert "x" * 4000 in prompt and "x" * 4001 not in prompt  # cut at the cap


async def test_empty_batch_makes_no_call() -> None:
    ex, m = extractor({"invoices": []})
    assert await ex.extract_many([]) == [] and m.calls == []


async def test_batches_and_single_extraction_fall_over_to_the_next_model() -> None:
    ex, m = extractor({"invoices": [invoice(1, "A")]}, ["m1", "m2"], fail=("m1",))
    await ex.extract_many(["a"])
    assert [c[0] for c in m.calls] == ["m1", "m2"]
    single, m2 = extractor(invoice(0, "S"), ["m1", "m2"], fail=("m1",))
    assert (await single.extract("text")).invoice_number == "S"
    assert [c[0] for c in m2.calls] == ["m1", "m2"]
