import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.api import auth, chat, conversations, documents, health
from app.config import get_settings
from app.db import make_engine
from app.services.storage import make_s3
from app.worker.deps import build_deps

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    s = get_settings()
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
    yield
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Groundwork", lifespan=lifespan)
    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(documents.router)
    app.include_router(conversations.router)
    app.include_router(chat.router)
    return app


app = create_app()
