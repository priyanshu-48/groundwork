import asyncio
import logging
from datetime import timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

log = logging.getLogger(__name__)

# attempts is incremented by claim(), so a job already at max_attempts has used its budget: fail
# it instead of requeueing, or a job that kills every worker that touches it would loop forever.
_REAP = text("""
UPDATE jobs SET
    status = (CASE WHEN attempts >= max_attempts THEN 'failed' ELSE 'queued' END)::job_status,
    locked_at = NULL, locked_by = NULL,
    last_error = 'worker lost (visibility timeout expired)'
WHERE status = 'running' AND locked_at < now() - make_interval(secs => :s)
""")


async def reap_stale(session: AsyncSession, older_than: timedelta) -> int:
    """Recover jobs whose worker died mid-run. Returns how many were touched."""
    result = await session.execute(_REAP, {"s": older_than.total_seconds()})
    return int(result.rowcount)  # type: ignore[attr-defined]


async def run_reaper(
    maker: async_sessionmaker[AsyncSession], interval_s: float, visibility_s: float
) -> None:
    """Loop forever; the worker runs this as a background task (wired up in M3)."""
    while True:
        try:
            async with maker.begin() as s:
                n = await reap_stale(s, timedelta(seconds=visibility_s))
            if n:
                log.warning("reaped %d stale jobs", n)
        except Exception:
            log.exception("reaper iteration failed")
        await asyncio.sleep(interval_s)
