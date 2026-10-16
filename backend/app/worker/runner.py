"""Worker process: `python -m app.worker.runner`. Claims jobs from the Postgres queue and runs them.
Scale by starting more processes; SKIP LOCKED keeps them from colliding."""

import asyncio
import contextlib
import logging
import os
import signal
import socket
import uuid

from app.config import get_settings
from app.services.ingestion import ingest_document, mark_failed
from app.services.parsing import PermanentError
from app.worker.deps import Deps, build_deps
from app.worker.queue import claim, complete, fail
from app.worker.reaper import run_reaper

log = logging.getLogger(__name__)


async def process_one(deps: Deps, worker_id: str) -> bool:
    """Claim and run one job. Returns False if the queue had nothing due."""
    async with deps.maker.begin() as session:  # commits the claim, so the lock is visible at once
        job = await claim(session, worker_id)
    if job is None:
        return False

    permanent = False
    try:
        if job.type != "ingest":
            raise PermanentError(f"Unknown job type {job.type!r}")
        await ingest_document(deps, uuid.UUID(job.payload["document_id"]))
    except PermanentError as e:
        error, permanent = str(e), True
    except Exception as e:
        log.exception("job %s failed (attempt %d/%d)", job.id, job.attempts, job.max_attempts)
        error = f"{type(e).__name__}: {e}"
    else:
        async with deps.maker.begin() as session:
            await complete(session, job.id)
        return True

    async with deps.maker.begin() as session:
        status = await fail(session, job.id, error, permanent=permanent)
    if status == "failed" and job.type == "ingest":
        await mark_failed(deps, uuid.UUID(job.payload["document_id"]), error)
    return True


async def run_worker(deps: Deps, worker_id: str, stop: asyncio.Event, poll_s: float = 1.0) -> None:
    while not stop.is_set():
        try:
            worked = await process_one(deps, worker_id)
        except Exception:
            log.exception("worker loop error")
            worked = False
        if not worked:  # idle: wait for the poll interval, but wake immediately on shutdown
            with contextlib.suppress(TimeoutError):
                await asyncio.wait_for(stop.wait(), poll_s)


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
    s = get_settings()
    deps, engine = build_deps(s)
    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        with contextlib.suppress(NotImplementedError):  # Windows has no loop signal handlers
            loop.add_signal_handler(sig, stop.set)
    worker_id = f"{socket.gethostname()}-{os.getpid()}"
    reaper = asyncio.create_task(
        run_reaper(deps.maker, s.reaper_interval_s, s.job_visibility_timeout_s)
    )
    log.info("worker %s started (ai_provider=%s)", worker_id, s.ai_provider)
    try:
        await run_worker(deps, worker_id, stop, s.worker_poll_s)
    finally:
        reaper.cancel()
        await engine.dispose()
        log.info("worker stopped")


if __name__ == "__main__":
    asyncio.run(main())
