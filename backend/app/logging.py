"""Structured JSON logs and per-request context.

One JSON object per line so logs can be searched by field (request_id, org_id, status). What is
deliberately never logged: request bodies, Authorization headers, emails, document text. The
request id ties a log line to the X-Request-ID response header a user can quote in a bug report."""

import json
import logging
import re
import sys
import time
import uuid
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

from starlette.datastructures import Headers, MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

request_id_var: ContextVar[str | None] = ContextVar("request_id", default=None)
org_id_var: ContextVar[str | None] = ContextVar("org_id", default=None)
job_id_var: ContextVar[str | None] = ContextVar("job_id", default=None)
document_id_var: ContextVar[str | None] = ContextVar("document_id", default=None)

_CONTEXT = (
    ("request_id", request_id_var),
    ("org_id", org_id_var),
    ("job_id", job_id_var),
    ("document_id", document_id_var),
)
_SAFE_ID = re.compile(r"^[A-Za-z0-9_-]{1,64}$")

access_log = logging.getLogger("groundwork.access")


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        out: dict[str, Any] = {
            "ts": datetime.fromtimestamp(record.created, UTC).isoformat(timespec="milliseconds"),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        for key, var in _CONTEXT:
            if (value := var.get()) is not None:
                out[key] = value
        fields = getattr(record, "fields", None)
        if isinstance(fields, dict):
            out.update(fields)
        if record.exc_info:
            out["exc"] = self.formatException(record.exc_info)
        return json.dumps(out, default=str)


def configure_logging(level: str = "INFO") -> None:
    """JSON to stderr for everything. Safe to call twice (replaces the handler)."""
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(level)
    for noisy in ("httpx", "httpcore", "google_genai", "urllib3", "botocore", "boto3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)  # one line per outbound call is noise


def clean_request_id(raw: str | None) -> str:
    """Keep a client-supplied id only if it is short and harmless (it ends up in logs and headers);
    otherwise generate one. Prevents log injection through newlines or huge values."""
    return raw if raw and _SAFE_ID.match(raw) else uuid.uuid4().hex


class RequestContextMiddleware:
    """Pure ASGI (no BaseHTTPMiddleware), so streaming responses are not buffered and context
    variables set by dependencies are still visible here after the response."""

    def __init__(self, app: ASGIApp, http_metrics: Any = None) -> None:
        self.app = app
        self.http_metrics = http_metrics

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        rid = clean_request_id(Headers(scope=scope).get("x-request-id"))
        rid_token = request_id_var.set(rid)
        org_token = org_id_var.set(None)
        started = time.perf_counter()
        status = 500

        async def send_with_id(message: Message) -> None:
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
                MutableHeaders(scope=message)["X-Request-ID"] = rid
            await send(message)

        try:
            await self.app(scope, receive, send_with_id)
        finally:
            ms = round((time.perf_counter() - started) * 1000, 1)
            route = getattr(scope.get("route"), "path", None) or "unmatched"
            access_log.log(
                logging.ERROR if status >= 500 else logging.INFO,
                "request",
                extra={
                    "fields": {
                        "method": scope["method"],
                        "path": scope["path"],
                        "route": route,
                        "status": status,
                        "duration_ms": ms,
                    }
                },
            )
            if self.http_metrics is not None:
                self.http_metrics.record(route, status, ms)
            org_id_var.reset(org_token)
            request_id_var.reset(rid_token)
