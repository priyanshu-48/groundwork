import asyncio
import hashlib
import math
import re
from collections.abc import Awaitable, Callable
from typing import Any, Literal, Protocol

from google.genai import types

from app.services.gemini import Throttle, call_with_retry

Task = Literal["document", "query"]
_TASK_TYPE = {"document": "RETRIEVAL_DOCUMENT", "query": "RETRIEVAL_QUERY"}


class EmbeddingError(Exception):
    pass


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str], task: Task) -> list[list[float]]: ...


def _normalize(v: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in v))
    return [x / n for x in v] if n else v


class FakeEmbeddingProvider:
    """Deterministic bag-of-words hashing: texts sharing words get similar vectors. Lets tests
    exercise real retrieval behaviour with no network and no key."""

    _TOKEN = re.compile(r"[a-z0-9]+")
    # Common words carry no signal; without dropping them every text looks alike.
    _STOP = frozenset(
        "a an the is are was be of in on at to for and or by with this that it as from what which "
        "who how does do shall any each".split()
    )

    def __init__(self, dims: int = 768) -> None:
        self.dims = dims

    async def embed(self, texts: list[str], task: Task) -> list[list[float]]:
        return [self._one(t) for t in texts]

    def _one(self, text: str) -> list[float]:
        v = [0.0] * self.dims
        for word in self._TOKEN.findall(text.lower()):
            if word in self._STOP:
                continue
            h = hashlib.sha256(word.encode()).digest()
            v[int.from_bytes(h[:4], "big") % self.dims] += 1.0 if h[4] & 1 else -1.0
        if not any(v):
            v[0] = 1.0
        return _normalize(v)


class GeminiEmbeddingProvider:
    """gemini-embedding-001 truncated to `dims` via Matryoshka. Vectors shorter than the native
    3072 dims are not unit-length, so we normalize (cosine search assumes comparable norms)."""

    def __init__(
        self,
        client: Any,
        model: str,
        dims: int = 768,
        batch_size: int = 50,
        max_tries: int = 4,
        sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep,
        throttle: Throttle | None = None,
    ) -> None:
        self._client, self._model, self._dims = client, model, dims
        self._throttle = throttle
        self._batch, self._max_tries, self._sleep = batch_size, max_tries, sleep

    async def embed(self, texts: list[str], task: Task) -> list[list[float]]:
        out: list[list[float]] = []
        for i in range(0, len(texts), self._batch):
            out += await self._embed_batch(texts[i : i + self._batch], _TASK_TYPE[task])
        return out

    async def _embed_batch(self, batch: list[str], task_type: str) -> list[list[float]]:
        cfg = types.EmbedContentConfig(task_type=task_type, output_dimensionality=self._dims)
        if self._throttle:
            await self._throttle.wait()
        try:
            resp = await call_with_retry(
                lambda: self._client.models.embed_content(
                    model=self._model, contents=batch, config=cfg
                ),
                max_tries=self._max_tries,
                sleep=self._sleep,
            )
        except Exception as e:
            raise EmbeddingError(f"Embedding request failed: {e}") from e
        vectors = [list(e.values) for e in resp.embeddings]
        if len(vectors) != len(batch) or any(len(v) != self._dims for v in vectors):
            raise EmbeddingError("Embedding response had unexpected shape")
        return [_normalize(v) for v in vectors]
