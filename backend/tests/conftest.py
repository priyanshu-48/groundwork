import asyncio
import os
import time
from collections.abc import Iterator
from typing import Any

import boto3
import pytest
from alembic.config import Config
from botocore.config import Config as BotoConfig
from fastapi.testclient import TestClient
from sqlalchemy import Row, text
from testcontainers.core.container import DockerContainer
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.config import get_settings
from app.db import make_engine

BUCKET = "test-bucket"
S3_KEY = "test-access-key"
S3_SECRET = "test-secret-key-123"
S3_IMAGE = "rustfs/rustfs:latest"  # MinIO's public images were removed; see docs/decisions/0001


@pytest.fixture(scope="session")
def pg() -> Iterator[PostgresContainer]:
    with PostgresContainer("pgvector/pgvector:pg16", driver="asyncpg") as c:
        yield c


@pytest.fixture(scope="session")
def s3() -> Iterator[str]:
    """Throwaway S3-compatible server; yields its endpoint URL with the test bucket created."""
    c = (
        DockerContainer(S3_IMAGE)
        .with_exposed_ports(9000)
        .with_env("RUSTFS_ACCESS_KEY", S3_KEY)
        .with_env("RUSTFS_SECRET_KEY", S3_SECRET)
    )
    with c:
        url = f"http://{c.get_container_host_ip()}:{c.get_exposed_port(9000)}"
        client = boto3.client(
            "s3",
            endpoint_url=url,
            aws_access_key_id=S3_KEY,
            aws_secret_access_key=S3_SECRET,
            region_name="us-east-1",
            config=BotoConfig(retries={"max_attempts": 1}),
        )
        for _ in range(30):  # process starts before it accepts S3 calls
            try:
                client.create_bucket(Bucket=BUCKET)
                break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError("S3 container never became ready")
        yield url


@pytest.fixture(scope="session")
def configured(pg: PostgresContainer, s3: str) -> Iterator[None]:
    os.environ.update(
        DATABASE_URL=pg.get_connection_url(),
        JWT_SECRET="integration-test-secret-32-bytes-minimum",
        S3_BUCKET=BUCKET,
        S3_ENDPOINT_URL=s3,
        S3_ACCESS_KEY=S3_KEY,
        S3_SECRET_KEY=S3_SECRET,
    )
    get_settings.cache_clear()
    command.upgrade(Config("alembic.ini"), "head")
    yield
    get_settings.cache_clear()


@pytest.fixture
def client(configured: None) -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app()) as c:  # context manager runs the lifespan
        yield c


@pytest.fixture
def sql(configured: None):  # type: ignore[no-untyped-def]
    """Run a raw SELECT against the test DB from sync tests (own engine, own event loop)."""

    def run(stmt: str, **params: object) -> list[Row[Any]]:
        async def go() -> list[Row[Any]]:
            engine = make_engine(get_settings().database_url)
            try:
                async with engine.connect() as conn:
                    return list((await conn.execute(text(stmt), params)).all())
            finally:
                await engine.dispose()

        return asyncio.run(go())

    return run
