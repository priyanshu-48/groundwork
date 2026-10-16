import uuid
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

PW = "a-long-enough-password"


def _pdf() -> bytes:
    return b"%PDF-1.4\n" + uuid.uuid4().bytes  # unique per call; M2 only checks the magic bytes


def _org(c: TestClient) -> tuple[dict[str, str], str]:
    r = c.post(
        "/auth/signup",
        json={"org_name": "Acme", "email": f"u-{uuid.uuid4().hex[:8]}@example.com", "password": PW},
    )
    h = {"Authorization": f"Bearer {r.json()['access_token']}"}
    return h, c.get("/auth/me", headers=h).json()["org_id"]


def _upload(c: TestClient, h: dict[str, str], data: bytes, kind: str = "contract"):  # type: ignore[no-untyped-def]
    return c.post(
        "/documents",
        headers=h,
        data={"kind": kind},
        files={"file": ("a.pdf", data, "application/pdf")},
    )


def test_same_file_twice_is_one_document_and_one_job(client: TestClient, sql) -> None:  # type: ignore[no-untyped-def]
    h, org_id = _org(client)
    data = _pdf()
    first, second = _upload(client, h, data), _upload(client, h, data)
    assert (first.status_code, second.status_code) == (201, 200)
    assert first.json()["id"] == second.json()["id"]
    assert first.json()["status"] == "pending"
    doc_id = first.json()["id"]
    assert sql("SELECT count(*) FROM documents WHERE org_id = :o", o=uuid.UUID(org_id))[0][0] == 1
    jobs = sql("SELECT type, status FROM jobs WHERE idempotency_key = :k", k=f"ingest:{doc_id}")
    assert [tuple(j) for j in jobs] == [("ingest", "queued")]


def test_file_lands_in_s3_at_deterministic_key(client: TestClient) -> None:
    h, org_id = _org(client)
    data = _pdf()
    sha = _upload(client, h, data).json()["sha256"]
    obj = client.app.state.s3.get_object(  # type: ignore[attr-defined]
        Bucket="test-bucket", Key=f"orgs/{org_id}/docs/{sha}.pdf"
    )
    assert obj["Body"].read() == data


def test_concurrent_identical_uploads_make_one_document(client: TestClient, sql) -> None:  # type: ignore[no-untyped-def]
    h, org_id = _org(client)
    data = _pdf()
    with ThreadPoolExecutor(4) as pool:
        codes = sorted(
            r.status_code for r in pool.map(lambda _: _upload(client, h, data), range(4))
        )
    assert codes.count(201) == 1 and codes.count(200) == 3
    assert sql("SELECT count(*) FROM documents WHERE org_id = :o", o=uuid.UUID(org_id))[0][0] == 1


def test_non_pdf_rejected(client: TestClient) -> None:
    h, _ = _org(client)
    assert _upload(client, h, b"hello, not a pdf").status_code == 415


def test_oversized_rejected(client: TestClient) -> None:
    h, _ = _org(client)
    assert _upload(client, h, b"%PDF-" + b"0" * (20 * 1024 * 1024)).status_code == 413


def test_requires_auth(client: TestClient) -> None:
    r = client.post("/documents", files={"file": ("a.pdf", _pdf(), "application/pdf")})
    assert r.status_code == 401
    assert client.get("/documents").status_code == 401


def test_orgs_are_isolated(client: TestClient) -> None:
    ha, _ = _org(client)
    hb, _ = _org(client)
    data = _pdf()
    a, b = _upload(client, ha, data), _upload(client, hb, data)
    assert (a.status_code, b.status_code) == (201, 201)  # same bytes, separate tenants
    assert a.json()["id"] != b.json()["id"]
    assert [d["id"] for d in client.get("/documents", headers=ha).json()] == [a.json()["id"]]
    assert [d["id"] for d in client.get("/documents", headers=hb).json()] == [b.json()["id"]]
