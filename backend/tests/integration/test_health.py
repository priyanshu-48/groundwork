import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.config import get_settings


def test_health_ok(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "db": "ok", "s3": "ok"}


def test_migration_enabled_pgvector(client: TestClient) -> None:
    import asyncio

    from app.db import make_engine

    async def q() -> object:
        engine = make_engine(
            get_settings().database_url
        )  # own engine: client's lives in another loop
        async with engine.connect() as conn:
            r = await conn.execute(text("SELECT extname FROM pg_extension WHERE extname='vector'"))
            out = r.scalar()
        await engine.dispose()
        return out

    assert asyncio.run(q()) == "vector"


def test_health_degraded_when_s3_missing(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("S3_BUCKET", "does-not-exist")
    get_settings.cache_clear()
    r = client.get("/health")
    assert r.status_code == 503
    assert r.json()["s3"] == "down" and r.json()["db"] == "ok"
    get_settings.cache_clear()
