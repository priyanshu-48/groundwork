"""Retrieval metrics. A rank is the 1-based position of the first relevant hit, or None."""

import math


def recall_at_k(ranks: list[int | None], k: int) -> float:
    if not ranks:
        return 0.0
    return sum(1 for r in ranks if r is not None and r <= k) / len(ranks)


def mrr_at_k(ranks: list[int | None], k: int) -> float:
    if not ranks:
        return 0.0
    return sum(1 / r for r in ranks if r is not None and r <= k) / len(ranks)


def percentile(values: list[float], p: float) -> float:
    """Linear interpolation between closest ranks (same as numpy's default)."""
    s = sorted(values)
    pos = (len(s) - 1) * p / 100
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)
