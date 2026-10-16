import asyncio
import random
import time
from collections.abc import Awaitable, Callable
from typing import Any

import httpx
from google import genai
from google.genai import types

from app.config import Settings


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
