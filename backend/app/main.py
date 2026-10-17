import dataclasses
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api import admin, auth, chat, conversations, documents, health, search
from app.config import get_settings
from app.db import make_engine
from app.logging import RequestContextMiddleware, configure_logging
from app.services.embedcache import CachedEmbedder
from app.services.metrics import HttpMetrics, parse_prices
from app.services.ratelimit import build_limits
from app.services.storage import make_s3
from app.worker.deps import build_deps

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    s = get_settings()
    configure_logging(s.log_level)
    if len(s.jwt_secret) < 32 or s.jwt_secret == "change-me":
        raise RuntimeError("JWT_SECRET must be a random string of at least 32 chars")
    app.state.engine = make_engine(s.database_url)
    app.state.sessions = async_sessionmaker(app.state.engine, expire_on_commit=False)
    app.state.s3 = make_s3(s)
    try:
        # Shares the API's connection pool. Uploads and listing keep working without a model key.
        app.state.agent_deps, _ = build_deps(s, app.state.engine)
    except SystemExit as e:  # AI_PROVIDER=gemini without GEMINI_API_KEY
        log.warning("chat disabled: %s", e)
        app.state.agent_deps = None
    if app.state.agent_deps is not None:
        # Query embeddings only; ingestion keeps the raw embedder (it never repeats a text).
        d = app.state.agent_deps
        app.state.agent_deps = dataclasses.replace(
            d, embedder=CachedEmbedder(d.embedder, s.embedding_model, s.query_embedding_cache_size)
        )
    app.state.limits = build_limits(s)
    app.state.model_prices = parse_prices(s.model_prices)
    yield
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Groundwork", lifespan=lifespan)
    app.state.http_metrics = HttpMetrics()
    app.add_middleware(RequestContextMiddleware, http_metrics=app.state.http_metrics)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(conversations.router)
    app.include_router(chat.router)
    app.include_router(search.router)
    app.include_router(admin.router)
    return app


app = create_app()
