"""GET /admin/metrics: operational numbers, behind a static token (docs/decisions/0012)."""

import hmac
from typing import Any

from fastapi import APIRouter, Header, HTTPException, Request

from app.config import get_settings
from app.services.metrics import agent_stats, queue_stats

router = APIRouter(tags=["admin"])


@router.get("/admin/metrics")
async def metrics(
    request: Request, x_admin_token: str | None = Header(default=None)
) -> dict[str, Any]:
    configured = get_settings().admin_token
    if not configured:
        raise HTTPException(404, "Not found")  # feature off: the route does not exist
    if x_admin_token is None or not hmac.compare_digest(x_admin_token, configured):
        raise HTTPException(401, "Invalid admin token")
    async with request.app.state.sessions() as session:
        return {
            "http": request.app.state.http_metrics.summary(),
            "agent": await agent_stats(session, request.app.state.model_prices),
            "queue": await queue_stats(session),
        }
