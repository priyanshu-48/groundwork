import math
from types import SimpleNamespace
from typing import Any

import pytest
from google.genai import errors

from app.services.embeddings import EmbeddingError, FakeEmbeddingProvider, GeminiEmbeddingProvider


def _cos(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=True))


async def test_fake_is_deterministic_768d_and_unit_norm() -> None:
    p = FakeEmbeddingProvider()
    (a,) = await p.embed(["late payment penalty"], "document")
    (b,) = await p.embed(["late payment penalty"], "document")
    assert a == b and len(a) == 768
    assert math.isclose(math.sqrt(sum(x * x for x in a)), 1.0, rel_tol=1e-9)


async def test_fake_related_text_scores_higher_than_unrelated() -> None:
    p = FakeEmbeddingProvider()
    q, near, far = await p.embed(
        ["late payment penalty clause", "penalty for late payment", "banana smoothie recipe"],
        "query",
    )
    assert _cos(q, near) > _cos(q, far)


class StubModels:
    def __init__(self, fail_times: int = 0, code: int = 429, dims: int = 4) -> None:
        self.fail_times, self.code, self.dims = fail_times, code, dims
        self.calls: list[tuple[int, str]] = []

    def embed_content(self, *, model: str, contents: list[str], config: Any) -> Any:
        self.calls.append((len(contents), config.task_type))
        if self.fail_times > 0:
            self.fail_times -= 1
            raise errors.APIError(self.code, {"error": {"message": "stub"}})
        vec = [3.0, 4.0] + [0.0] * (self.dims - 2)
        return SimpleNamespace(embeddings=[SimpleNamespace(values=vec) for _ in contents])


def _provider(models: StubModels, max_tries: int = 4, sleeps: list[float] | None = None):  # type: ignore[no-untyped-def]
    async def fake_sleep(s: float) -> None:
        if sleeps is not None:
            sleeps.append(s)

    return GeminiEmbeddingProvider(
        SimpleNamespace(models=models), "m", dims=4, max_tries=max_tries, sleep=fake_sleep
    )


async def test_gemini_batches_of_50_and_normalizes() -> None:
    m = StubModels()
    out = await _provider(m).embed([f"t{i}" for i in range(120)], "document")
    assert [n for n, _ in m.calls] == [50, 50, 20]
    assert {t for _, t in m.calls} == {"RETRIEVAL_DOCUMENT"}
    assert len(out) == 120 and out[0] == pytest.approx([0.6, 0.8, 0.0, 0.0])


async def test_gemini_query_task_type() -> None:
    m = StubModels()
    await _provider(m).embed(["q"], "query")
    assert m.calls[0][1] == "RETRIEVAL_QUERY"


async def test_gemini_retries_429_with_growing_backoff() -> None:
    m, sleeps = StubModels(fail_times=2), []
    await _provider(m, sleeps=sleeps).embed(["x"], "document")
    assert len(m.calls) == 3 and len(sleeps) == 2 and sleeps[1] > sleeps[0]


async def test_gemini_gives_up_after_max_tries() -> None:
    m = StubModels(fail_times=99)
    with pytest.raises(EmbeddingError):
        await _provider(m, max_tries=3).embed(["x"], "document")
    assert len(m.calls) == 3


async def test_gemini_does_not_retry_client_errors() -> None:
    m = StubModels(fail_times=99, code=400)
    with pytest.raises(EmbeddingError):
        await _provider(m).embed(["x"], "document")
    assert len(m.calls) == 1


async def test_gemini_rejects_wrong_dimensionality() -> None:
    m = StubModels(dims=8)
    with pytest.raises(EmbeddingError):
        await _provider(m).embed(["x"], "document")
