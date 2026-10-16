from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api import health
from app.config import get_settings
from app.db import make_engine
from app.services.storage import make_s3


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    s = get_settings()
    app.state.engine = make_engine(s.database_url)
    app.state.s3 = make_s3(s)
    yield
    await app.state.engine.dispose()


def create_app() -> FastAPI:
    app = FastAPI(title="Groundwork", lifespan=lifespan)
    app.include_router(health.router)
    return app


app = create_app()
