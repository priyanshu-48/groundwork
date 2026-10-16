from collections.abc import AsyncIterator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.config import get_settings
from app.db import make_engine
from app.services.embeddings import FakeEmbeddingProvider
from app.services.extraction import FakeInvoiceExtractor
from app.services.storage import make_s3
from app.worker.deps import Deps


@pytest.fixture
async def deps(configured: None) -> AsyncIterator[Deps]:
    """Real Postgres + real S3-compatible server, fake AI providers (no network)."""
    s = get_settings()
    engine = make_engine(s.database_url)
    d = Deps(
        maker=async_sessionmaker(engine, expire_on_commit=False),
        s3=make_s3(s),
        bucket=s.s3_bucket,
        embedder=FakeEmbeddingProvider(),
        extractor=FakeInvoiceExtractor(),
        settings=s,
    )
    async with d.maker.begin() as session:
        await session.execute(text("TRUNCATE jobs"))  # isolate queue state per test
    yield d
    await engine.dispose()


@pytest.fixture(scope="module")
def small(tmp_path_factory: pytest.TempPathFactory) -> tuple[dict, Path]:
    """A small generated corpus (6 contracts, 24 invoices) shared by a test module."""
    from evals.generate_corpus import build_ground_truth, render_corpus

    out = tmp_path_factory.mktemp("small-corpus")
    gt = build_ground_truth(seed=42, n_vendors=6, n_invoices=24)
    render_corpus(gt, out, seed=42)
    return gt, out
