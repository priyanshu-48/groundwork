import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.agent.llm import FakeLLM, say
from app.config import get_settings
from app.services.ratelimit import SlidingWindowLimiter
from tests.helpers import make_pdf
from tests.integration.test_chat_api import PW, chat, ingest, new_conv, set_llm, signup
from tests.integration.test_observability import set_limits


@pytest.fixture
def demo_on(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    # unique per test: the test database is shared, and the cap counts everything in the demo org
    monkeypatch.setenv("DEMO_ACCOUNT_EMAIL", f"demo-owner-{uuid.uuid4().hex[:8]}@example.com")
    monkeypatch.setenv("DEMO_DAILY_CHAT_CAP", "3")
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


def make_demo_org(c: TestClient) -> str:
    """The loader account that owns the corpus; returns its org id."""
    email = get_settings().demo_account_email
    r = c.post("/auth/signup", json={"org_name": "Demo Co", "email": email, "password": PW})
    assert r.status_code == 201, r.text
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    return str(c.get("/auth/me", headers=h).json()["org_id"])


def demo_login(c: TestClient) -> dict[str, str]:
    r = c.post("/auth/demo")
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_demo_is_off_unless_configured(client: TestClient) -> None:
    assert client.post("/auth/demo").status_code == 404
    assert client.get("/meta").json()["demo_available"] is False


@pytest.mark.usefixtures("demo_on")
def test_demo_login_joins_the_demo_org_as_a_demo_user(client: TestClient) -> None:
    org = make_demo_org(client)
    assert client.get("/meta").json()["demo_available"] is True
    h = demo_login(client)
    me = client.get("/auth/me", headers=h).json()
    assert me["org_id"] == org and me["demo"] is True
    other = demo_login(client)
    assert client.get("/auth/me", headers=other).json()["user_id"] != me["user_id"]


@pytest.mark.usefixtures("demo_on")
def test_a_missing_demo_account_is_a_503_not_a_crash(client: TestClient) -> None:
    assert client.post("/auth/demo").status_code == 503  # configured, but nobody loaded it yet


@pytest.mark.usefixtures("demo_on")
def test_demo_users_can_read_and_search_but_not_upload(client: TestClient) -> None:
    org = make_demo_org(client)
    ingest(client, org, "Payment Terms. Net 45 applies to Acme Corp invoices.")
    h = demo_login(client)
    assert len(client.get("/documents", headers=h).json()) == 1
    hits = client.post("/search", headers=h, json={"query": "payment terms Net 45"}).json()["hits"]
    assert hits and hits[0]["filename"] == "acme-contract.pdf"
    up = client.post(
        "/documents",
        headers=h,
        data={"kind": "other"},
        files={"file": ("x.pdf", make_pdf(["hello"]), "application/pdf")},
    )
    assert up.status_code == 403 and "read-only" in up.json()["detail"]


@pytest.mark.usefixtures("demo_on")
def test_demo_visitors_do_not_see_each_others_conversations(client: TestClient) -> None:
    make_demo_org(client)
    a, b = demo_login(client), demo_login(client)
    conv_a = new_conv(client, a)
    set_llm(client, FakeLLM([say("hi")]))
    assert chat(client, a, conv_a).status_code == 200
    assert [c["id"] for c in client.get("/conversations", headers=a).json()] == [conv_a]
    assert client.get("/conversations", headers=b).json() == []
    assert client.get(f"/conversations/{conv_a}/messages", headers=b).status_code == 404
    assert chat(client, b, conv_a).status_code == 404


@pytest.mark.usefixtures("demo_on")
def test_daily_cap_is_shared_across_visitors_and_explains_itself(client: TestClient) -> None:
    make_demo_org(client)
    set_llm(client, FakeLLM([say("ok")] * 10))
    visitors = [demo_login(client) for _ in range(3)]
    convs = [new_conv(client, h) for h in visitors]
    for h, c in zip(visitors, convs, strict=True):  # cap is 3: three visitors use it up
        assert chat(client, h, c).status_code == 200
    r = chat(client, visitors[0], convs[0])
    assert r.status_code == 429 and int(r.headers["retry-after"]) >= 1
    assert "daily question limit" in r.json()["detail"]


@pytest.mark.usefixtures("demo_on")
def test_the_cap_does_not_apply_to_real_users_or_other_orgs(client: TestClient) -> None:
    make_demo_org(client)
    set_llm(client, FakeLLM([say("ok")] * 10))
    h, _ = signup(client)  # an ordinary customer
    conv = new_conv(client, h)
    for _ in range(5):
        assert chat(client, h, conv).status_code == 200


@pytest.mark.usefixtures("demo_on")
def test_demo_login_is_throttled_per_ip(client: TestClient) -> None:
    make_demo_org(client)
    set_limits(client, demo=SlidingWindowLimiter(2))
    assert client.post("/auth/demo").status_code == 200
    assert client.post("/auth/demo").status_code == 200
    r = client.post("/auth/demo")
    assert r.status_code == 429 and "retry-after" in r.headers


@pytest.mark.usefixtures("demo_on")
def test_ordinary_tokens_are_not_demo_and_demo_flag_cannot_be_forged(client: TestClient) -> None:
    make_demo_org(client)
    h, _ = signup(client)
    assert client.get("/auth/me", headers=h).json()["demo"] is False
    from datetime import timedelta

    from app.services.security import create_token

    forged = create_token(
        uuid.uuid4(),
        uuid.uuid4(),
        "wrong-secret-wrong-secret-wrong-secret",
        timedelta(hours=1),
        demo=False,
    )
    assert client.get("/auth/me", headers={"Authorization": f"Bearer {forged}"}).status_code == 401
