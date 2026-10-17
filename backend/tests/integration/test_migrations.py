import asyncio
import os

from alembic.config import Config
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.config import get_settings

AGENT_TABLES = {"conversations", "messages", "agent_runs", "agent_steps"}


async def _tables(url: str) -> set[str]:
    engine = create_async_engine(url)
    try:
        async with engine.connect() as c:
            rows = await c.execute(
                text("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
            )
            return {r[0] for r in rows}
    finally:
        await engine.dispose()


async def _create_db(admin_url: str, name: str) -> None:
    engine = create_async_engine(admin_url, isolation_level="AUTOCOMMIT")
    try:
        async with engine.connect() as c:
            await c.execute(text(f"CREATE DATABASE {name}"))
    finally:
        await engine.dispose()


def test_every_migration_applies_from_scratch_and_the_agent_one_round_trips(
    pg: PostgresContainer, configured: None
) -> None:
    admin_url = pg.get_connection_url()
    scratch = admin_url.rsplit("/", 1)[0] + "/migration_check"
    asyncio.run(_create_db(admin_url, "migration_check"))
    cfg = Config("alembic.ini")
    previous = os.environ["DATABASE_URL"]
    os.environ["DATABASE_URL"] = scratch
    get_settings.cache_clear()
    try:
        command.upgrade(cfg, "head")
        assert AGENT_TABLES <= asyncio.run(_tables(scratch))
        assert "contracts" in asyncio.run(_tables(scratch))
        command.downgrade(cfg, "0006")
        tables = asyncio.run(_tables(scratch))
        assert "contracts" not in tables and AGENT_TABLES <= tables
        command.downgrade(cfg, "0005")
        assert not AGENT_TABLES & asyncio.run(_tables(scratch))
        command.upgrade(cfg, "head")
        tables = asyncio.run(_tables(scratch))
        assert AGENT_TABLES <= tables and "contracts" in tables
    finally:
        os.environ["DATABASE_URL"] = previous
        get_settings.cache_clear()
