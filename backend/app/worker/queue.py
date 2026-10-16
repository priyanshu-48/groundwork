"""Postgres job queue. Why Postgres: the job row commits in the same transaction as the document
row (no "document saved, job lost"), and FOR UPDATE SKIP LOCKED gives safe multi-worker claiming
without extra infrastructure. All functions run inside the caller's transaction."""

import uuid
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.job import Job


@dataclass(frozen=True)
class ClaimedJob:
    id: uuid.UUID
    type: str
    payload: dict[str, Any]
    attempts: int
    max_attempts: int


async def enqueue(
    session: AsyncSession,
    type: str,
    payload: dict[str, Any],
    idempotency_key: str | None = None,
    max_attempts: int = 5,
    run_after_in: timedelta | None = None,
) -> uuid.UUID | None:
    """Returns the new job id, or None if a job with this idempotency_key already exists."""
    values: dict[str, Any] = {
        "id": uuid.uuid4(),
        "type": type,
        "payload": payload,
        "status": "queued",
        "attempts": 0,
        "max_attempts": max_attempts,
        "idempotency_key": idempotency_key,
    }
    if run_after_in is not None:
        values["run_after"] = text("now() + make_interval(secs => :d)").bindparams(
            d=run_after_in.total_seconds()
        )
    stmt = (
        pg_insert(Job)
        .values(**values)
        .on_conflict_do_nothing(index_elements=["idempotency_key"])
        .returning(Job.id)
    )
    return (await session.execute(stmt)).scalar_one_or_none()


_CLAIM = text("""
UPDATE jobs SET status = 'running', locked_at = now(), locked_by = :worker,
                attempts = attempts + 1
WHERE id = (
    SELECT id FROM jobs
    WHERE status = 'queued' AND run_after <= now()
    ORDER BY run_after
    FOR UPDATE SKIP LOCKED
    LIMIT 1)
RETURNING id, type, payload, attempts, max_attempts
""")


async def claim(session: AsyncSession, worker: str) -> ClaimedJob | None:
    """Atomically take one due job. SKIP LOCKED makes a concurrent claimer pass over rows another
    transaction is already updating, so two workers can never get the same job."""
    row = (await session.execute(_CLAIM, {"worker": worker})).one_or_none()
    return ClaimedJob(*row) if row else None


async def complete(session: AsyncSession, job_id: uuid.UUID) -> None:
    await session.execute(
        text("UPDATE jobs SET status = 'done', locked_at = NULL, locked_by = NULL WHERE id = :i"),
        {"i": job_id},
    )


_FAIL = text("""
UPDATE jobs SET
    status = (CASE WHEN retry THEN 'queued' ELSE 'failed' END)::job_status,
    run_after = CASE WHEN retry
                     THEN now() + make_interval(secs => power(2, attempts) + random())
                     ELSE run_after END,
    locked_at = NULL, locked_by = NULL, last_error = :err
FROM (SELECT id AS jid, (NOT CAST(:perm AS boolean) AND attempts < max_attempts) AS retry
      FROM jobs WHERE id = :i) AS r
WHERE jobs.id = r.jid
RETURNING jobs.status
""")


async def fail(
    session: AsyncSession, job_id: uuid.UUID, error: str, permanent: bool = False
) -> str:
    """Retry with exponential backoff (2^attempts s + jitter) until max_attempts, then give up.
    permanent=True skips the retries (retrying a corrupt file cannot help). Returns the job's
    new status; the caller marks the owning document failed on 'failed'."""
    params = {"i": job_id, "err": error[:2000], "perm": permanent}
    return str((await session.execute(_FAIL, params)).scalar_one())
