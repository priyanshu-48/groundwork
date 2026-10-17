import asyncio
import json
import logging
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.agent.llm import FakeLLM, say
from app.config import get_settings
from app.db import make_engine
from app.logging import JsonFormatter, access_log
from app.services.ratelimit import ConcurrencyLimiter, Limits, SlidingWindowLimiter
from tests.integration.test_chat_api import PW, chat, ingest, new_conv, set_llm, signup

ADMIN = {"X-Admin-Token": "test-admin-token"}


def set_limits(c: TestClient, **kw: Any) -> None:
    base: dict[str, Any] = {
        "chat": SlidingWindowLimiter(1000),
        "chat_concurrent": ConcurrencyLimiter(1000),
        "search": SlidingWindowLimiter(1000),
        "login": SlidingWindowLimiter(1000),
        "signup": SlidingWindowLimiter(1000),
    }
    base.update(kw)
    c.app.state.limits = Limits(**base)  # type: ignore[attr-defined]


class Grab(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.lines: list[dict[str, Any]] = []
        self.raw: list[str] = []

    def emit(self, record: logging.LogRecord) -> None:
        rendered = JsonFormatter().format(record)
        self.raw.append(rendered)
        self.lines.append(json.loads(rendered))


@pytest.fixture
def grab() -> Any:
    h = Grab()
    access_log.addHandler(h)
    old = access_log.level
    access_log.setLevel(logging.INFO)
    yield h
    access_log.removeHandler(h)
    access_log.setLevel(old)


# ----------------------------------------------------------------- request ids and logs


def test_request_id_is_generated_echoed_and_sanitised(client: TestClient) -> None:
    assert len(client.get("/health").headers["x-request-id"]) == 32
    echoed = client.get("/health", headers={"X-Request-ID": "my-trace_1"})
    assert echoed.headers["x-request-id"] == "my-trace_1"
    assert client.get("/health", headers={"X-Request-ID": "a b"}).headers["x-request-id"] != "a b"


def test_access_line_has_org_and_request_id_and_nothing_sensitive(
    client: TestClient, grab: Grab
) -> None:
    email = f"secret-{uuid.uuid4().hex[:6]}@example.com"
    r = client.post("/auth/signup", json={"org_name": "Acme", "email": email, "password": PW})
    token = r.json()["access_token"]
    me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}", "X-Request-ID": "t-1"})
    org = me.json()["org_id"]

    line = next(ln for ln in grab.lines if ln["request_id"] == "t-1")
    assert (line["method"], line["route"], line["status"]) == ("GET", "/auth/me", 200)
    assert line["org_id"] == org and line["duration_ms"] >= 0
    assert len([ln for ln in grab.lines if ln["route"] == "/auth/signup"]) == 1
    everything = " ".join(grab.raw)
    for forbidden in (PW, email, token, "Bearer"):
        assert forbidden not in everything


# ----------------------------------------------------------------- rate limits


def test_chat_rate_limit_is_per_org_and_has_retry_after(client: TestClient) -> None:
    set_limits(client, chat=SlidingWindowLimiter(2))
    ha, _ = signup(client)
    hb, _ = signup(client)
    ca, cb = new_conv(client, ha), new_conv(client, hb)
    set_llm(client, FakeLLM([say("ok")] * 10))
    assert chat(client, ha, ca).status_code == 200
    assert chat(client, ha, ca).status_code == 200
    r = chat(client, ha, ca)
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1
    assert "try again" in r.json()["detail"]
    assert chat(client, hb, cb).status_code == 200  # other tenant unaffected


def test_concurrency_slot_is_freed_after_a_run(client: TestClient) -> None:
    set_limits(client, chat_concurrent=ConcurrencyLimiter(1))
    h, _ = signup(client)
    conv = new_conv(client, h)
    set_llm(client, FakeLLM([say("one"), say("two")]))
    assert chat(client, h, conv).status_code == 200
    assert chat(client, h, conv).status_code == 200  # would be 429 if the slot had leaked


def test_concurrency_cap_rejects_a_second_simultaneous_run(client: TestClient) -> None:
    lim = ConcurrencyLimiter(1)
    set_limits(client, chat_concurrent=lim)
    h, org = signup(client)
    conv = new_conv(client, h)
    assert lim.acquire(org) is not None  # a run already in flight
    r = chat(client, h, conv)
    assert r.status_code == 429 and "retry-after" in r.headers


def test_slot_is_freed_when_the_run_fails(client: TestClient) -> None:
    class Broken:
        async def generate_stream(self, *_a: object, **_k: object):  # type: ignore[no-untyped-def]
            raise RuntimeError("boom")
            yield ""  # pragma: no cover

        generate = generate_stream

    lim = ConcurrencyLimiter(1)
    set_limits(client, chat_concurrent=lim)
    h, org = signup(client)
    conv = new_conv(client, h)
    set_llm(client, Broken())
    chat(client, h, conv)
    assert lim.acquire(org) is not None


def test_login_and_signup_are_throttled_per_ip(client: TestClient) -> None:
    set_limits(client, login=SlidingWindowLimiter(2), signup=SlidingWindowLimiter(1))
    body = {"org_name": "A", "email": f"{uuid.uuid4().hex[:8]}@example.com", "password": PW}
    assert client.post("/auth/signup", json=body).status_code == 201
    r = client.post("/auth/signup", json={**body, "email": "other@example.com"})
    assert r.status_code == 429 and "retry-after" in r.headers
    bad = {"email": body["email"], "password": "wrong-password-123"}
    assert client.post("/auth/login", json=bad).status_code == 401
    assert client.post("/auth/login", json=bad).status_code == 401
    assert client.post("/auth/login", json=bad).status_code == 429


# ----------------------------------------------------------------- search endpoint


def test_search_requires_auth_and_validates(client: TestClient) -> None:
    assert client.post("/search", json={"query": "x"}).status_code == 401
    h, _ = signup(client)
    assert client.post("/search", headers=h, json={"query": "x", "top_k": 11}).status_code == 422
    assert client.post("/search", headers=h, json={"query": ""}).status_code == 422
    assert client.post("/search", headers=h, json={"query": "x", "kind": "memo"}).status_code == 422


def test_search_is_org_scoped_and_returns_file_page_snippet(client: TestClient) -> None:
    ha, org_a = signup(client)
    hb, _ = signup(client)
    ingest(client, org_a, "Payment Terms. Net 45 applies to Acme Corp invoices.")
    q = {"query": "payment terms Net 45"}
    hits = client.post("/search", headers=ha, json=q).json()["hits"]
    assert hits and hits[0]["filename"] == "acme-contract.pdf" and hits[0]["page"] == 1
    assert "Net 45" in hits[0]["snippet"]
    assert client.post("/search", headers=hb, json=q).json()["hits"] == []
    wrong_kind = client.post("/search", headers=ha, json={**q, "kind": "invoice"})
    assert wrong_kind.json()["hits"] == []


def test_second_identical_search_does_not_call_the_embedder(client: TestClient) -> None:
    h, _ = signup(client)
    cache = client.app.state.agent_deps.embedder  # type: ignore[attr-defined]
    inner = cache._inner
    calls: list[str] = []

    class Spy:
        async def embed(self, texts: list[str], task: str) -> list[list[float]]:
            calls.extend(texts)
            return await inner.embed(texts, task)  # type: ignore[no-any-return]

    cache._inner = Spy()
    q = {"query": f"unique question {uuid.uuid4().hex}"}
    client.post("/search", headers=h, json=q)
    client.post("/search", headers=h, json=q)
    assert len(calls) == 1


def test_search_is_rate_limited_per_org(client: TestClient) -> None:
    set_limits(client, search=SlidingWindowLimiter(1))
    h, _ = signup(client)
    assert client.post("/search", headers=h, json={"query": "a"}).status_code == 200
    assert client.post("/search", headers=h, json={"query": "a"}).status_code == 429


# ----------------------------------------------------------------- admin metrics


def test_admin_metrics_auth(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    assert client.get("/admin/metrics").status_code == 401
    assert client.get("/admin/metrics", headers={"X-Admin-Token": "nope"}).status_code == 401
    h, _ = signup(client)
    assert client.get("/admin/metrics", headers=h).status_code == 401  # a user JWT is not enough
    assert client.get("/admin/metrics", headers=ADMIN).status_code == 200
    monkeypatch.setenv("ADMIN_TOKEN", "")
    get_settings.cache_clear()
    try:
        assert client.get("/admin/metrics", headers=ADMIN).status_code == 404
    finally:
        monkeypatch.undo()
        get_settings.cache_clear()


def test_admin_metrics_sections_cost_and_no_tenant_text(client: TestClient) -> None:
    h, _ = signup(client)
    conv = new_conv(client, h)
    set_llm(client, FakeLLM([say("The secret answer text")]))
    assert chat(client, h, conv, "the secret question text").status_code == 200

    async def seed_priced() -> None:
        engine = make_engine(get_settings().database_url)
        async with engine.begin() as conn:
            mid = (
                await conn.execute(text("SELECT id FROM messages ORDER BY created_at DESC LIMIT 1"))
            ).scalar()
            await conn.execute(
                text(
                    "INSERT INTO agent_runs (id, message_id, model, prompt_tokens, "
                    "completion_tokens, latency_ms, status) VALUES "
                    "(gen_random_uuid(), :m, 'priced-model', 1000000, 500000, 1234, 'ok')"
                ),
                {"m": mid},
            )
        await engine.dispose()

    asyncio.run(seed_priced())
    body = client.get("/admin/metrics", headers=ADMIN).json()
    assert {"http", "agent", "queue"} <= body.keys()
    models = {m["model"]: m for m in body["agent"]["by_model"]}
    assert models["priced-model"]["estimated_cost_usd"] == "3.000000"  # 1M*$1 + 0.5M*$4, exact
    assert body["agent"]["estimated_cost_usd"] is None  # another model ran with no price
    assert body["agent"]["runs"] >= 2 and "queue_depth" in body["queue"]
    assert body["http"]["overall"]["count"] >= 1
    dumped = json.dumps(body)
    assert "secret answer text" not in dumped and "secret question text" not in dumped
