import asyncio
import random
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
