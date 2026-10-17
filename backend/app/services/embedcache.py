import asyncio
from collections import OrderedDict

from app.services.embeddings import EmbeddingProvider, Task


class CachedEmbedder:
    """LRU cache in front of an embedder, for QUERY embeddings only.

    The same question asked twice should not spend embedding quota twice. The embedding of a fixed
    text under a fixed model never changes, so entries never need to expire; the cache is bounded
    and per process. Document embeddings are never cached (ingestion embeds each chunk once).
    Concurrent identical misses share one call instead of stampeding the API."""

    def __init__(self, inner: EmbeddingProvider, model: str, max_size: int = 1000) -> None:
        self._inner, self._model, self._max = inner, model, max_size
        self._cache: OrderedDict[str, list[float]] = OrderedDict()
        self._inflight: dict[str, asyncio.Future[list[float]]] = {}
        self.hits = 0
        self.misses = 0

    def _key(self, text: str) -> str:
        return f"{self._model}\x00{text}"

    async def embed(self, texts: list[str], task: Task) -> list[list[float]]:
        if task != "query":
            return await self._inner.embed(texts, task)
        return [await self._one(t) for t in texts]

    async def _one(self, text: str) -> list[float]:
        key = self._key(text)
        if key in self._cache:
            self._cache.move_to_end(key)
            self.hits += 1
            return self._cache[key]
        if key in self._inflight:
            self.hits += 1  # someone else is already paying for this one
            return await self._inflight[key]
        self.misses += 1
        future: asyncio.Future[list[float]] = asyncio.get_running_loop().create_future()
        self._inflight[key] = future
        try:
            (vector,) = await self._inner.embed([text], "query")
        except BaseException as e:
            future.set_exception(e)
            future.exception()  # mark retrieved: nobody may be waiting, and that must not warn
            raise
        else:
            future.set_result(vector)
            self._cache[key] = vector
            while len(self._cache) > self._max:
                self._cache.popitem(last=False)
            return vector
        finally:
            del self._inflight[key]
