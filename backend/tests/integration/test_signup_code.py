import uuid
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from tests.integration.test_chat_api import PW


@pytest.fixture
def code_required(monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("SIGNUP_CODE", "open-sesame-123")
    get_settings.cache_clear()
    yield
    monkeypatch.undo()
    get_settings.cache_clear()


def body(**extra: object) -> dict[str, object]:
    return {
        "org_name": "Acme",
        "email": f"u-{uuid.uuid4().hex[:8]}@example.com",
        "password": PW,
        **extra,
    }


def test_signup_is_open_when_no_code_is_configured(client: TestClient) -> None:
    assert client.post("/auth/signup", json=body()).status_code == 201
    assert client.get("/meta").json()["signup_code_required"] is False


@pytest.mark.usefixtures("code_required")
def test_signup_needs_the_right_code_when_configured(client: TestClient) -> None:
    assert client.get("/meta").json()["signup_code_required"] is True
    for bad in (
        {},
        {"invite_code": ""},
        {"invite_code": "wrong"},
        {"invite_code": "open-sesame-12"},
    ):
        r = client.post("/auth/signup", json=body(**bad))
        assert r.status_code == 403, bad
        assert "open-sesame" not in r.text  # never echo the secret
    assert client.post("/auth/signup", json=body(invite_code="open-sesame-123")).status_code == 201


@pytest.mark.usefixtures("code_required")
def test_a_rejected_code_creates_no_account_and_login_needs_no_code(client: TestClient) -> None:
    b = body(invite_code="open-sesame-123")
    assert client.post("/auth/signup", json=b).status_code == 201
    login = {"email": b["email"], "password": PW}
    assert client.post("/auth/login", json=login).status_code == 200  # no code on login
    again = body(invite_code="nope")
    again["email"] = b["email"]
    assert client.post("/auth/signup", json=again).status_code == 403  # not 409: no email probing
