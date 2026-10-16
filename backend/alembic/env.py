import asyncio

from sqlalchemy.engine import Connection

from alembic import context
from app.config import get_settings
from app.db import make_engine

# M0 has no tables; later milestones set target_metadata to their models' metadata.
target_metadata = None


def _run(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def _run_online() -> None:
    engine = make_engine(get_settings().database_url)
    async with engine.connect() as conn:
        await conn.run_sync(_run)
    await engine.dispose()


asyncio.run(_run_online())
