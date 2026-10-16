import asyncio

from fastapi import APIRouter, Request, Response
from sqlalchemy import text

from app.config import get_settings
from app.services.storage import s3_ok

router = APIRouter()


async def _db_ok(request: Request, timeout_s: float) -> bool:
    try:
        async with asyncio.timeout(timeout_s), request.app.state.engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return False
    return True


@router.get("/health")
async def health(request: Request, response: Response) -> dict[str, str]:
    s = get_settings()
    db, s3 = await asyncio.gather(
        _db_ok(request, s.check_timeout_s),
        s3_ok(request.app.state.s3, s.s3_bucket),
    )
    if not (db and s3):
        response.status_code = 503
    return {
        "status": "ok" if db and s3 else "degraded",
        "db": "ok" if db else "down",
        "s3": "ok" if s3 else "down",
    }
