import asyncio
from collections.abc import AsyncIterator
from datetime import timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.config import get_settings
from app.db import make_engine
from app.worker.queue import claim, complete, enqueue, fail
from app.worker.reaper import reap_stale

Maker = async_sessionmaker[AsyncSession]


@pytest.fixture
async def maker(configured: None) -> AsyncIterator[Maker]:
    engine = make_engine(get_settings().database_url)
    m = async_sessionmaker(engine, expire_on_commit=False)
    async with m.begin() as s:
        await s.execute(text("TRUNCATE jobs"))
    yield m
    await engine.dispose()


async def _row(maker: Maker, job_id: object) -> dict[str, object]:
    async with maker() as s:
        r = await s.execute(text("SELECT * FROM jobs WHERE id = :i"), {"i": job_id})
        return dict(r.mappings().one())


async def test_two_workers_process_each_job_exactly_once(maker: Maker) -> None:
    async with maker.begin() as s:
        ids = [await enqueue(s, "t", {"n": n}) for n in range(20)]
    processed: list[object] = []

    async def worker(name: str) -> None:
        while True:
            async with maker.begin() as s:
                job = await claim(s, name)
            if job is None:
                return
            await asyncio.sleep(0.01)  # hold the job so the workers really interleave
            processed.append(job.id)
            async with maker.begin() as s:
                await complete(s, job.id)

    await asyncio.gather(worker("w1"), worker("w2"))

    assert len(processed) == 20
    assert sorted(processed, key=str) == sorted(ids, key=str)  # no job twice, none lost
    async with maker() as s:
        done = (await s.execute(text("SELECT count(*) FROM jobs WHERE status='done'"))).scalar()
    assert done == 20


async def test_future_run_after_is_not_claimed(maker: Maker) -> None:
    async with maker.begin() as s:
        await enqueue(s, "t", {}, run_after_in=timedelta(hours=1))
    async with maker.begin() as s:
        assert await claim(s, "w") is None


async def test_duplicate_idempotency_key_is_one_job(maker: Maker) -> None:
    async with maker.begin() as s:
        first = await enqueue(s, "t", {}, idempotency_key="k")
        second = await enqueue(s, "t", {}, idempotency_key="k")
    assert first is not None and second is None
    async with maker() as s:
        assert (await s.execute(text("SELECT count(*) FROM jobs"))).scalar() == 1


async def test_fail_backs_off_then_gives_up(maker: Maker) -> None:
    async with maker.begin() as s:
        job_id = await enqueue(s, "t", {}, max_attempts=2)
    async with maker.begin() as s:
        job = await claim(s, "w")
    assert job is not None and job.attempts == 1
    async with maker.begin() as s:
        assert await fail(s, job_id, "boom") == "queued"
    row = await _row(maker, job_id)
    assert row["status"] == "queued" and row["last_error"] == "boom"
    async with maker.begin() as s:
        assert await claim(s, "w") is None  # backing off, not claimable yet
        await s.execute(text("UPDATE jobs SET run_after = now()"))
    async with maker.begin() as s:
        job = await claim(s, "w")
    assert job is not None and job.attempts == 2
    async with maker.begin() as s:
        assert await fail(s, job_id, "boom again") == "failed"


async def test_reaper_requeues_stale_running_job(maker: Maker) -> None:
    async with maker.begin() as s:
        job_id = await enqueue(s, "t", {})
    async with maker.begin() as s:
        assert await claim(s, "dead-worker") is not None
        # a fresh lock is left alone
    async with maker.begin() as s:
        assert await reap_stale(s, timedelta(minutes=5)) == 0
    async with maker.begin() as s:
        await s.execute(text("UPDATE jobs SET locked_at = now() - interval '10 minutes'"))
    async with maker.begin() as s:
        assert await reap_stale(s, timedelta(minutes=5)) == 1
    assert (await _row(maker, job_id))["status"] == "queued"
    async with maker.begin() as s:
        assert await claim(s, "w2") is not None  # another worker can now take it


async def test_reaper_fails_poison_job_at_max_attempts(maker: Maker) -> None:
    async with maker.begin() as s:
        job_id = await enqueue(s, "t", {}, max_attempts=1)
    async with maker.begin() as s:
        await claim(s, "w")
        await s.execute(text("UPDATE jobs SET locked_at = now() - interval '10 minutes'"))
    async with maker.begin() as s:
        await reap_stale(s, timedelta(minutes=5))
    assert (await _row(maker, job_id))["status"] == "failed"
