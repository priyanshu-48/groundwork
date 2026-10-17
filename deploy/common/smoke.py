"""End-to-end smoke test against a running deployment (stdlib only, so it runs anywhere).

Usage:  python3 deploy/common/smoke.py https://1-2-3-4.sslip.io [--code INVITE] [--admin-token TOKEN]
(or SMOKE_CODE / ADMIN_TOKEN in the environment, which keeps secrets out of shell history).

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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("base")
    ap.add_argument("--code", default=os.environ.get("SMOKE_CODE", ""))
    ap.add_argument("--admin-token", default=os.environ.get("ADMIN_TOKEN", ""))
    a = ap.parse_args()
    base = a.base.rstrip("/")
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
    step("answer is cited", "event: citations" in text and '"ref": "C1"' in text)
    step("run finished ok", '"status": "ok"' in text.split("event: done")[-1])

    if a.admin_token:
        status, _, _ = call(base, "/api/admin/metrics")
        step("metrics need a token", status in (401, 404), f"status {status}")
        status, _, body = call(base, "/api/admin/metrics", headers={"X-Admin-Token": a.admin_token})
        step("metrics with token", status == 200 and "queue" in json.loads(body))
    print("ALL PASSED")


if __name__ == "__main__":
    main()
