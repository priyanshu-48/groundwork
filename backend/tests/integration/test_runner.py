import asyncio

from app.worker.deps import Deps
from app.worker.runner import run_worker
from tests.helpers import make_pdf, new_org, scalar, seed, words


async def test_run_worker_drains_the_queue_then_stops_on_signal(deps: Deps) -> None:
    org = await new_org(deps)
    ids = [await seed(deps, org, make_pdf([words(40, f"d{i}x")])) for i in range(3)]
    stop = asyncio.Event()
    task = asyncio.create_task(run_worker(deps, "w1", stop, poll_s=0.05))

    async def all_ready() -> bool:
        n = await scalar(
            deps,
            "SELECT count(*) FROM documents WHERE status = 'ready' AND id = ANY(:ids)",
            ids=ids,
        )
        return bool(n == 3)

    for _ in range(100):
        if await all_ready():
            break
        await asyncio.sleep(0.1)
    stop.set()
    await asyncio.wait_for(task, timeout=5)  # exits promptly, no hang

    assert await all_ready()
