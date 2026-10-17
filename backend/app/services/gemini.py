import asyncio
import logging
import random
import re
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from google import genai
from google.genai import types

from app.config import Settings

log = logging.getLogger(__name__)


def make_client(s: Settings) -> genai.Client:
    """Per-request timeout is set on the client so no call can hang a worker."""
    return genai.Client(
        api_key=s.gemini_api_key,
        http_options=types.HttpOptions(timeout=int(s.ai_timeout_s * 1000)),
    )


def is_retryable(e: Exception) -> bool:
    """429 and 5xx are worth retrying; other 4xx mean our request is wrong and never will work."""
    code = getattr(e, "code", None)
    if isinstance(code, int):
        if code == 429 and "PerDay" in str(e):
            return False  # daily quota: retrying within seconds only burns more requests
        return code == 429 or code >= 500
    return isinstance(e, TimeoutError | httpx.TransportError)


async def call_with_retry[T](
    fn: Callable[[], T],
    *,
    max_tries: int = 4,
    sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep,
) -> T:
    """Run a blocking SDK call in a thread; bounded retries with exponential backoff + jitter."""
    for attempt in range(1, max_tries + 1):
        try:
            return await asyncio.to_thread(fn)
        except Exception as e:
            if attempt == max_tries or not is_retryable(e):
                raise
            await sleep(2 ** (attempt - 1) + random.random())
    raise AssertionError("unreachable")


class Throttle:
    """Spaces calls at least `min_interval_s` apart so bulk loads stay inside per-minute quotas."""

    def __init__(
        self,
        min_interval_s: float,
        clock: Callable[[], float] = time.monotonic,
        sleep: Callable[[float], Awaitable[Any]] = asyncio.sleep,
    ) -> None:
        self._interval, self._clock, self._sleep = min_interval_s, clock, sleep
        self._next_at = 0.0
        self._lock = asyncio.Lock()

    async def wait(self) -> None:
        if self._interval <= 0:
            return
        async with self._lock:
            now = self._clock()
            if now < self._next_at:
                await self._sleep(self._next_at - now)
            self._next_at = max(now, self._next_at) + self._interval


class LLMUnavailable(Exception):
    """Every model in the chain is out of quota or failing."""


_RETRY_DELAY = re.compile(r"retryDelay['\"]?\s*:\s*['\"]?(\d+(?:\.\d+)?)s")


def retry_delay_s(e: Exception) -> float | None:
    """The server's own 'try again in N seconds' hint (RetryInfo), when it sent one."""
    m = _RETRY_DELAY.search(str(e))
    return float(m.group(1)) if m else None


def _fall_over_seconds(e: Exception) -> float | None:
    """How long to stop using a model after this error, or None if another model cannot help.

    Quota (429), overload (5xx) and a missing model (404) are properties of one model, so the next
    model may well succeed. A 400/401/403 means our request or key is wrong: every model would
    fail the same way, so we raise instead of burning the rest of the chain."""
    code = getattr(e, "code", None)
    if not isinstance(code, int):
        return 60.0 if isinstance(e, TimeoutError | httpx.TransportError) else None
    if code == 429:
        return retry_delay_s(e) or (3600.0 if "PerDay" in str(e) else 60.0)
    if code == 404:
        return float("inf")  # a model that does not exist will not appear mid-run
    if code >= 500:
        return 60.0
    return None


class ModelChain:
    """Ordered generation models with per-model memory of when each is usable again.

    Free-tier quotas are per model, so a chain adds the allowances up. Used for the agent and for
    invoice extraction, never for embeddings: vectors from different embedding models are not
    comparable, so mixing them would silently corrupt search."""

    def __init__(self, models: list[str], clock: Callable[[], float] = time.monotonic) -> None:
        if not models:
            raise ValueError("ModelChain needs at least one model")
        self.models = list(models)
        self._clock = clock
        self._blocked_until: dict[str, float] = {}

    def available(self) -> list[str]:
        now = self._clock()
        return [m for m in self.models if self._blocked_until.get(m, 0.0) <= now]

    async def run[T](self, call: Callable[[str], Awaitable[T]]) -> tuple[str, T]:
        """Try each usable model in order; return (model that answered, its result)."""
        last: Exception | None = None
        for model in self.available():
            try:
                return model, await call(model)
            except Exception as e:
                wait = _fall_over_seconds(e)
                if wait is None:
                    raise
                self._blocked_until[model] = self._clock() + wait
                log.warning("model %s unavailable for %.0fs (%s); trying next", model, wait, e)
                last = e
        raise LLMUnavailable(
            f"no usable model left in the chain ({', '.join(self.models)})"
        ) from last
