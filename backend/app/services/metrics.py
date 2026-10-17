"""Operational numbers for GET /admin/metrics: HTTP latency (in process), agent runs and the job
queue (from the database). Counts and timings only; never tenant content."""

import json
import math
import time
from collections import deque
from decimal import Decimal
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def percentile(values: list[float], p: float) -> float:
    """Linear interpolation between closest ranks."""
    s = sorted(values)
    if not s:
        return 0.0
    pos = (len(s) - 1) * p / 100
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


class HttpMetrics:
    """The last `size` requests, grouped by route template (not raw path, so ids do not explode
    the cardinality). Lives in memory: resets on restart and covers one process."""

    def __init__(self, size: int = 10_000) -> None:
        self._samples: deque[tuple[str, int, float]] = deque(maxlen=size)
        self.started_at = time.time()

    def record(self, route: str, status: int, ms: float) -> None:
        self._samples.append((route, status, ms))

    @staticmethod
    def _summarize(rows: list[tuple[str, int, float]]) -> dict[str, Any]:
        ms = [r[2] for r in rows]
        errors = sum(1 for r in rows if r[1] >= 500)
        return {
            "count": len(rows),
            "error_rate": round(errors / len(rows), 4) if rows else 0.0,
            "p50_ms": round(percentile(ms, 50), 1),
            "p95_ms": round(percentile(ms, 95), 1),
            "p99_ms": round(percentile(ms, 99), 1),
        }

    def summary(self) -> dict[str, Any]:
        rows = list(self._samples)
        by_route: dict[str, list[tuple[str, int, float]]] = {}
        for r in rows:
            by_route.setdefault(r[0], []).append(r)
        return {
            "note": "last requests of this process only; resets on restart",
            "since": self.started_at,
            "overall": self._summarize(rows),
            "routes": {k: self._summarize(v) for k, v in sorted(by_route.items())},
        }


def parse_prices(raw: str) -> dict[str, tuple[Decimal, Decimal]]:
    """MODEL_PRICES='{"model-name": [usd_per_million_input_tokens, usd_per_million_output]}'.
    Empty means no prices configured: costs are then reported as null, never guessed."""
    if not raw.strip():
        return {}
    out: dict[str, tuple[Decimal, Decimal]] = {}
    for model, pair in json.loads(raw).items():
        price_in, price_out = pair
        out[model] = (Decimal(str(price_in)), Decimal(str(price_out)))
    return out


async def agent_stats(
    session: AsyncSession, prices: dict[str, tuple[Decimal, Decimal]], hours: int = 24
) -> dict[str, Any]:
    window = f"created_at > now() - interval '{int(hours)} hours'"  # int(): not user input anyway
    head = (
        await session.execute(
            text(f"""
        SELECT count(*) AS runs,
               coalesce(sum(prompt_tokens), 0) AS tokens_in,
               coalesce(sum(completion_tokens), 0) AS tokens_out,
               percentile_cont(0.5) WITHIN GROUP (ORDER BY latency_ms) AS p50,
               percentile_cont(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95
        FROM agent_runs WHERE {window}""")  # noqa: S608
        )
    ).one()
    by_status = {
        r.status: r.n
        for r in await session.execute(
            text(f"SELECT status, count(*) AS n FROM agent_runs WHERE {window} GROUP BY status")  # noqa: S608
        )
    }
    models = (
        await session.execute(
            text(f"""
        SELECT coalesce(model, 'unknown') AS model, count(*) AS runs,
               sum(prompt_tokens) AS tokens_in, sum(completion_tokens) AS tokens_out
        FROM agent_runs WHERE {window} GROUP BY 1 ORDER BY runs DESC""")  # noqa: S608
        )
    ).all()
    avg_steps = (
        await session.execute(
            text(f"""
        SELECT avg(n) FROM (
            SELECT count(s.id) AS n FROM agent_runs r
            LEFT JOIN agent_steps s ON s.run_id = r.id
            WHERE r.{window} GROUP BY r.id) t""")  # noqa: S608
        )
    ).scalar()

    per_model: list[dict[str, Any]] = []
    total_cost: Decimal | None = Decimal(0)
    for m in models:
        price = prices.get(m.model)
        cost = (
            (Decimal(m.tokens_in) * price[0] + Decimal(m.tokens_out) * price[1])
            / Decimal(1_000_000)
            if price
            else None
        )
        total_cost = None if cost is None or total_cost is None else total_cost + cost
        per_model.append(
            {
                "model": m.model,
                "runs": m.runs,
                "tokens_in": int(m.tokens_in),
                "tokens_out": int(m.tokens_out),
                "estimated_cost_usd": None
                if cost is None
                else str(cost.quantize(Decimal("0.000001"))),
            }
        )
    return {
        "window_hours": hours,
        "runs": head.runs,
        "by_status": by_status,
        "error_rate": round(by_status.get("error", 0) / head.runs, 4) if head.runs else 0.0,
        "latency_ms": {"p50": round(head.p50 or 0, 1), "p95": round(head.p95 or 0, 1)},
        "tokens_in": int(head.tokens_in),
        "tokens_out": int(head.tokens_out),
        "avg_tool_steps": round(float(avg_steps or 0), 2),
        "by_model": per_model,
        # null unless every model that ran has a configured price; free-tier use is billed $0
        "estimated_cost_usd": None
        if total_cost is None or not models
        else str(total_cost.quantize(Decimal("0.000001"))),
    }


async def queue_stats(session: AsyncSession) -> dict[str, Any]:
    jobs = {
        r.status: r.n
        for r in await session.execute(
            text("SELECT status, count(*) AS n FROM jobs GROUP BY status")
        )
    }
    oldest = (
        await session.execute(
            text(
                "SELECT extract(epoch FROM now() - min(run_after)) FROM jobs "
                "WHERE status = 'queued' AND run_after <= now()"
            )
        )
    ).scalar()
    stale = (
        await session.execute(
            text(
                "SELECT count(*) FROM jobs WHERE status = 'running' "
                "AND locked_at < now() - interval '5 minutes'"
            )
        )
    ).scalar()
    docs = {
        r.status: r.n
        for r in await session.execute(
            text("SELECT status, count(*) AS n FROM documents GROUP BY status")
        )
    }
    return {
        "jobs": jobs,
        "queue_depth": jobs.get("queued", 0),
        "oldest_due_job_age_s": round(float(oldest), 1) if oldest is not None else 0.0,
        "stale_running_jobs": stale,
        "documents": docs,
    }
