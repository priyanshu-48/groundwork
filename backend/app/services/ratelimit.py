"""In-process rate limiting: a sliding window per key, and a cap on concurrent work per key.

Per process on purpose (ponytail: one API process today). With several API processes each would
allow the full limit, so the effective limit multiplies; Postgres or Redis is the upgrade."""

import math
import time
import uuid
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass

from fastapi import HTTPException, Request

from app.config import Settings


class SlidingWindowLimiter:
    def __init__(
        self, limit: int, window_s: float = 60.0, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self.limit, self.window_s, self._clock = limit, window_s, clock
        self._hits: dict[str, deque[float]] = {}
        self._calls = 0

    def check(self, key: str) -> float | None:
        """None if the call is allowed (and counted); otherwise seconds until it would be."""
        now = self._clock()
        self._calls += 1
        if self._calls % 256 == 0:
            # before fetching `key`'s deque, or its hit would land on a dropped one
            self._prune(now)
        hits = self._hits.setdefault(key, deque())
        while hits and hits[0] <= now - self.window_s:
            hits.popleft()
        if len(hits) >= self.limit:
            return max(0.0, hits[0] + self.window_s - now)
        hits.append(now)
        return None

    def _prune(self, now: float) -> None:
        """Forget keys with no recent hits so memory does not grow with the number of tenants."""
        for key in [k for k, h in self._hits.items() if not h or h[-1] <= now - self.window_s]:
            del self._hits[key]


class ConcurrencyLimiter:
    """At most `limit` holders per key. A slot older than `max_hold_s` is reclaimed, so a request
    that dies before it can release (client gone before the stream starts) never leaks it."""

    def __init__(
        self, limit: int, max_hold_s: float = 300.0, clock: Callable[[], float] = time.monotonic
    ) -> None:
        self.limit, self.max_hold_s, self._clock = limit, max_hold_s, clock
        self._held: dict[str, dict[str, float]] = {}

    def acquire(self, key: str) -> str | None:
        now = self._clock()
        held = self._held.setdefault(key, {})
        for token in [t for t, at in held.items() if at <= now - self.max_hold_s]:
            del held[token]
        if len(held) >= self.limit:
            return None
        token = uuid.uuid4().hex
        held[token] = now
        return token

    def release(self, key: str, token: str) -> None:
        held = self._held.get(key)
        if held is not None:
            held.pop(token, None)  # idempotent
            if not held:
                del self._held[key]


@dataclass
class Limits:
    chat: SlidingWindowLimiter
    chat_concurrent: ConcurrencyLimiter
    search: SlidingWindowLimiter
    login: SlidingWindowLimiter
    signup: SlidingWindowLimiter


def build_limits(s: Settings) -> Limits:
    return Limits(
        chat=SlidingWindowLimiter(s.chat_rate_limit_per_min),
        chat_concurrent=ConcurrencyLimiter(s.chat_max_concurrent),
        search=SlidingWindowLimiter(s.search_rate_limit_per_min),
        login=SlidingWindowLimiter(s.login_rate_limit_per_min),
        signup=SlidingWindowLimiter(s.signup_rate_limit_per_min),
    )


def get_limits(request: Request) -> Limits:
    limits: Limits = request.app.state.limits
    return limits


def too_many(retry_after: float, what: str) -> HTTPException:
    seconds = max(1, math.ceil(retry_after))
    return HTTPException(
        429,
        f"Too many {what}. Please try again in {seconds} s.",
        headers={"Retry-After": str(seconds)},
    )


def client_ip(request: Request) -> str:
    """The real client when uvicorn runs with --proxy-headers behind our own proxy."""
    return request.client.host if request.client else "unknown"
