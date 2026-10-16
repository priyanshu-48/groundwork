from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def make_engine(url: str) -> AsyncEngine:
    # pool_pre_ping: survive DB restarts without surfacing a stale-connection error.
    return create_async_engine(url, pool_pre_ping=True)
