import uuid
from datetime import timedelta

from fastapi.testclient import TestClient

from app.config import get_settings
from app.services.security import create_token

PW = "a-long-enough-password"


def _email() -> str:
    return f"user-{uuid.uuid4().hex[:8]}@example.com"


def _signup(c: TestClient, email: str | None = None) -> tuple[str, str]:
    email = email or _email()
    r = c.post("/auth/signup", json={"org_name": "Acme", "email": email, "password": PW})
    assert r.status_code == 201, r.text
    return email, r.json()["access_token"]


def _me(c: TestClient, token: str | None) -> object:
    h = {"Authorization": f"Bearer {token}"} if token else {}
    return c.get("/auth/me", headers=h)


def test_signup_then_login(client: TestClient) -> None:
    email, _ = _signup(client)
    r = client.post("/auth/login", json={"email": email, "password": PW})
    assert r.status_code == 200
    assert r.json()["token_type"] == "bearer"


def test_login_email_is_case_insensitive(client: TestClient) -> None:
    email, _ = _signup(client, "Mixed.Case@Example.com")
    r = client.post("/auth/login", json={"email": email.upper(), "password": PW})
    assert r.status_code == 200


def test_duplicate_email_409(client: TestClient) -> None:
    email, _ = _signup(client)
    r = client.post("/auth/signup", json={"org_name": "B", "email": email, "password": PW})
    assert r.status_code == 409


def test_weak_password_422(client: TestClient) -> None:
    r = client.post("/auth/signup", json={"org_name": "A", "email": _email(), "password": "short"})
    assert r.status_code == 422


def test_invalid_login_is_indistinguishable(client: TestClient) -> None:
    email, _ = _signup(client)
    wrong_pw = client.post("/auth/login", json={"email": email, "password": "nope-nope-nope"})
    unknown = client.post("/auth/login", json={"email": _email(), "password": PW})
    assert wrong_pw.status_code == unknown.status_code == 401
    assert wrong_pw.json() == unknown.json()


def test_me_requires_token(client: TestClient) -> None:
    assert _me(client, None).status_code == 401  # type: ignore[attr-defined]
    assert _me(client, "garbage").status_code == 401  # type: ignore[attr-defined]


def test_me_rejects_expired_token(client: TestClient) -> None:
    t = create_token(uuid.uuid4(), uuid.uuid4(), get_settings().jwt_secret, timedelta(seconds=-1))
    assert _me(client, t).status_code == 401  # type: ignore[attr-defined]


def test_me_returns_org_from_token_and_orgs_differ(client: TestClient) -> None:
    _, t1 = _signup(client)
    _, t2 = _signup(client)
    a = _me(client, t1).json()  # type: ignore[attr-defined]
    b = _me(client, t2).json()  # type: ignore[attr-defined]
    assert a["org_id"] != b["org_id"]
    assert a["user_id"] != b["user_id"]
