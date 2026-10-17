import asyncio

import pytest

from app.services.embedcache import CachedEmbedder
from app.services.embeddings import FakeEmbeddingProvider


class Counting(FakeEmbeddingProvider):
    def __init__(self) -> None:
        super().__init__()
        self.calls: list[tuple[list[str], str]] = []
        self.gate: asyncio.Event | None = None

    async def embed(self, texts, task):  # type: ignore[no-untyped-def,override]
        self.calls.append((texts, task))
        if self.gate:
            await self.gate.wait()
        return await super().embed(texts, task)


async def test_repeated_query_is_embedded_once() -> None:
    inner = Counting()
    c = CachedEmbedder(inner, "m")
    a = await c.embed(["net 45?"], "query")
    b = await c.embed(["net 45?"], "query")
    assert a == b and len(inner.calls) == 1 and (c.hits, c.misses) == (1, 1)


async def test_documents_are_never_cached() -> None:
    inner = Counting()
    c = CachedEmbedder(inner, "m")
    await c.embed(["chunk"], "document")
    await c.embed(["chunk"], "document")
    assert len(inner.calls) == 2


async def test_least_recently_used_entry_is_evicted() -> None:
    inner = Counting()
    c = CachedEmbedder(inner, "m", max_size=2)
    for q in ("a", "b", "a", "c"):  # a is refreshed, so b is the one evicted
        await c.embed([q], "query")
    n = len(inner.calls)
    await c.embed(["a"], "query")
    assert len(inner.calls) == n
    await c.embed(["b"], "query")
    assert len(inner.calls) == n + 1


async def test_concurrent_identical_queries_share_one_call() -> None:
    inner = Counting()
    inner.gate = asyncio.Event()
    c = CachedEmbedder(inner, "m")
    tasks = [asyncio.create_task(c.embed(["same"], "query")) for _ in range(5)]
    await asyncio.sleep(0)
    await asyncio.sleep(0)
    inner.gate.set()
    results = await asyncio.gather(*tasks)
    assert len(inner.calls) == 1 and all(r == results[0] for r in results)


async def test_failures_are_not_cached() -> None:
    class Boom(FakeEmbeddingProvider):
        n = 0

        async def embed(self, texts, task):  # type: ignore[no-untyped-def,override]
            Boom.n += 1
            if Boom.n == 1:
                raise RuntimeError("quota")
            return await super().embed(texts, task)

    c = CachedEmbedder(Boom(), "m")
    with pytest.raises(RuntimeError):
        await c.embed(["q"], "query")
    assert len(await c.embed(["q"], "query")) == 1  # retried, not served from a cached error
