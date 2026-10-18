"""End-to-end smoke test against a running deployment (stdlib only, so it runs anywhere).

Usage:  python3 deploy/common/smoke.py https://1-2-3-4.sslip.io [--code INVITE] [--admin-token TOKEN]
(or SMOKE_CODE / ADMIN_TOKEN in the environment, which keeps secrets out of shell history).
With --demo it checks the public demo workspace instead (no invite code needed): demo login,
read-only uploads, a loaded corpus, and cited answers to real questions.

Creates a throwaway org, uploads a small PDF, waits until it is ingested, asks one question and checks
the stream ends with a cited answer. With real Gemini this uses a handful of free-tier calls."""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

PDF = Path(__file__).resolve().parents[2] / "frontend" / "e2e" / "fixtures" / "net45.pdf"


def call(base: str, path: str, *, method: str = "GET", body: bytes | None = None,
         headers: dict[str, str] | None = None, timeout: float = 30) -> tuple[int, dict[str, str], bytes]:
    req = urllib.request.Request(base + path, data=body, method=method, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, {k.lower(): v for k, v in r.headers.items()}, r.read()
    except urllib.error.HTTPError as e:
        return e.code, {k.lower(): v for k, v in e.headers.items()}, e.read()


def step(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}{('  ' + detail) if detail else ''}")
    if not ok:
        sys.exit(1)


def multipart(filename: str, data: bytes, fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = uuid.uuid4().hex
    parts = [f'--{boundary}\r\nContent-Disposition: form-data; name="{k}"\r\n\r\n{v}\r\n'.encode()
             for k, v in fields.items()]
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="file"; filename="{filename}"\r\n'
        f"Content-Type: application/pdf\r\n\r\n".encode() + data + b"\r\n"
    )
    parts.append(f"--{boundary}--\r\n".encode())
    return b"".join(parts), f"multipart/form-data; boundary={boundary}"


def ask(base: str, auth: dict[str, str], question: str) -> str:
    """Asks one question in a fresh conversation; returns the raw event stream text."""
    j = {"Content-Type": "application/json"}
    _, _, body = call(base, "/api/conversations", method="POST", body=b"{}", headers={**auth, **j})
    conv = json.loads(body)["id"]
    payload = json.dumps({"content": question}).encode()
    status, _, body = call(base, f"/api/chat/{conv}/messages", method="POST", body=payload,
                           headers={**auth, **j}, timeout=180)
    step(f"chat streams: {question[:48]}...", status == 200 and "event: done" in body.decode(), f"status {status}")
    return body.decode()


def citations(stream: str) -> list[dict[str, object]]:
    """The cited sources of an answer (any ref: which Cn holds the clause varies by question)."""
    for block in stream.split("\n\n"):
        if block.startswith("event: citations"):
            return list(json.loads(block.split("data: ", 1)[1])["items"])
    return []


def step_evidence(stream: str) -> list[dict[str, object]]:
    """Evidence attached to finished tool steps (the rows behind a computed answer)."""
    found: list[dict[str, object]] = []
    for block in stream.split("\n\n"):
        if block.startswith("event: step"):
            data = json.loads(block.split("data: ", 1)[1])
            if data.get("status") == "ok" and data.get("evidence"):
                found.append(data["evidence"])
    return found


def answer_text(stream: str) -> str:
    for block in stream.split("\n\n"):
        if block.startswith("event: answer"):
            return str(json.loads(block.split("data: ", 1)[1])["text"])
    return ""


def demo_checks(base: str) -> None:
    status, _, body = call(base, "/api/meta")
    meta = json.loads(body)
    step("demo is available", status == 200 and meta.get("demo_available") is True, str(meta))
    status, _, body = call(base, "/api/auth/demo", method="POST")
    step("demo login", status == 200, f"status {status}")
    auth = {"Authorization": f"Bearer {json.loads(body)['access_token']}"}
    status, _, body = call(base, "/api/auth/me", headers=auth)
    step("token is a demo token", status == 200 and json.loads(body)["demo"] is True)
    status, _, body = call(base, "/api/documents?limit=100", headers=auth)
    docs = json.loads(body)
    step("demo workspace has documents", status == 200 and len(docs) >= 20, f"{len(docs)} on first page")
    data, ctype = multipart("net45.pdf", PDF.read_bytes(), {"kind": "contract"})
    status, _, _ = call(base, "/api/documents", method="POST", body=data, headers={**auth, "Content-Type": ctype})
    step("uploads are refused", status == 403, f"status {status}")

    stream = ask(base, auth, "What is the termination notice period in the Kestrel Security contract?")
    cites = citations(stream)
    step(
        "contract answer is cited from the Kestrel contract",
        any("kestrel" in str(c.get("filename", "")) for c in cites),
        ", ".join(f"{c.get('filename')} p{c.get('page')}" for c in cites),
    )
    step("contract answer mentions days", "day" in answer_text(stream).lower(), answer_text(stream)[:80])
    stream = ask(base, auth, "How much did Ironbridge Facilities bill us between 2025-11-01 and 2025-11-30?")
    text = answer_text(stream)
    step("aggregate answer has a figure", any(ch.isdigit() for ch in text), text[:80])
    evidence = [e for e in step_evidence(stream) if e.get("kind") == "invoices"]
    step("aggregate answer comes with evidence rows", bool(evidence) and bool(evidence[0]["rows"]))
    totals = evidence[0]["totals"]
    shown = ", ".join(f"{cur} {amount}" for cur, amount in dict(totals).items())  # type: ignore[call-overload]
    step(
        "the evidence total is the figure in the answer",
        any(str(amount) in text.replace(",", "") for amount in dict(totals).values()),  # type: ignore[call-overload]
        shown,
    )
    step("run finished ok", '"status": "ok"' in stream.split("event: done")[-1])
    print("DEMO ALL PASSED")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--demo", action="store_true", help="check the public demo workspace instead")
    ap.add_argument("--code", default=os.environ.get("SMOKE_CODE", ""))
    ap.add_argument("--admin-token", default=os.environ.get("ADMIN_TOKEN", ""))
    a = ap.parse_args()
    base = a.base.rstrip("/")
    if a.demo:
        demo_checks(base)
        return
    j = {"Content-Type": "application/json"}

    status, headers, body = call(base, "/api/health")
    step("health", status == 200 and json.loads(body)["status"] == "ok", body.decode()[:80])
    step("request id header", "x-request-id" in headers)
    status, _, body = call(base, "/api/meta")
    meta = json.loads(body)
    step("meta", status == 200, str(meta))

    email = f"smoke-{uuid.uuid4().hex[:8]}@example.com"
    signup = {"org_name": "Smoke", "email": email, "password": "smoke-" + uuid.uuid4().hex}
    if a.code:
        signup["invite_code"] = a.code
    status, _, body = call(base, "/api/auth/signup", method="POST", body=json.dumps(signup).encode(), headers=j)
    if meta.get("signup_code_required") and not a.code:
        step("signup without code is refused", status == 403)
        sys.exit("pass --code to continue")
    step("signup", status == 201, f"status {status}")
    auth = {"Authorization": f"Bearer {json.loads(body)['access_token']}"}

    data, ctype = multipart("net45.pdf", PDF.read_bytes(), {"kind": "contract"})
    status, _, body = call(base, "/api/documents", method="POST", body=data, headers={**auth, "Content-Type": ctype})
    step("upload", status in (200, 201), f"status {status}")
    deadline = time.time() + 240
    state = "pending"
    while time.time() < deadline and state not in ("ready", "failed"):
        time.sleep(3)
        _, _, body = call(base, "/api/documents", headers=auth)
        state = json.loads(body)[0]["status"]
    step("document ingested", state == "ready", state)

    _, _, body = call(base, "/api/conversations", method="POST", body=b"{}", headers={**auth, **j})
    conv = json.loads(body)["id"]
    ask = json.dumps({"content": "What are the payment terms?"}).encode()
    status, _, body = call(base, f"/api/chat/{conv}/messages", method="POST", body=ask,
                           headers={**auth, **j}, timeout=180)
    text = body.decode()
    step("chat streams", status == 200 and "event: done" in text, f"status {status}")
    step("answer is cited", len(citations(text)) > 0)
    step("run finished ok", '"status": "ok"' in text.split("event: done")[-1])

    if a.admin_token:
        status, _, _ = call(base, "/api/admin/metrics")
        step("metrics need a token", status in (401, 404), f"status {status}")
        status, _, body = call(base, "/api/admin/metrics", headers={"X-Admin-Token": a.admin_token})
        step("metrics with token", status == 200 and "queue" in json.loads(body))
    print("ALL PASSED")


if __name__ == "__main__":
    main()
