"""Upload the generated corpus to a running stack and wait until every document is ingested.

Run (from backend/, API + worker up):  uv run python ../evals/load_corpus.py
Credentials come from EVAL_EMAIL / EVAL_PASSWORD (a local eval-only account is created if needed).
Against a real deployment: set a strong EVAL_PASSWORD (the local default is refused) and, if signup
is gated, EVAL_INVITE_CODE. Pass these as environment variables, never on the command line.
Re-running is safe: uploads are idempotent, so already-loaded files are skipped by the server.
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
PASSWORD = os.environ.get("EVAL_PASSWORD", "eval-local-only-password")


async def _retry(fn):  # type: ignore[no-untyped-def]
    """Retry transport errors. Polling every 5 s lands exactly on uvicorn's 5 s keep-alive timeout,
    so a reused connection is sometimes already closed: harmless, just reconnect."""
    for attempt in range(1, 6):
        try:
            return await fn()
        except httpx.TransportError:
            if attempt == 5:
                raise
            await asyncio.sleep(0.5 * attempt)


def _is_local(api: str) -> bool:
    return any(h in api for h in ("localhost", "127.0.0.1", "[::1]"))


async def _auth(c: httpx.AsyncClient, email: str, invite_code: str = "") -> dict[str, str]:
    body = {"email": email, "password": PASSWORD}
    extra = {"invite_code": invite_code} if invite_code else {}
    r = await c.post("/auth/signup", json={**body, **extra, "org_name": "Eval Org"})
    if r.status_code == 409:
        r = await c.post("/auth/login", json=body)
    r.raise_for_status()
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


async def _upload(c, h, sem, path: Path, kind: str) -> None:  # type: ignore[no-untyped-def]
    data = path.read_bytes()
    async with sem:
        r = await _retry(
            lambda: c.post(
                "/documents",
                headers=h,
                data={"kind": kind},
                files={"file": (path.name, data, "application/pdf")},
            )
        )
        r.raise_for_status()


async def _statuses(c: httpx.AsyncClient, h: dict[str, str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    offset = 0
    while True:
        r = await _retry(
            lambda: c.get("/documents", headers=h, params={"limit": 100, "offset": offset})
        )
        page = r.json()
        for d in page:
            counts[d["status"]] = counts.get(d["status"], 0) + 1
        if len(page) < 100:
            return counts
        offset += 100


async def _main(a: argparse.Namespace) -> int:
    gt = json.loads(a.ground_truth.read_text(encoding="utf8"))
    files = [
        (a.corpus / "contracts" / v["contract"]["filename"], "contract") for v in gt["vendors"]
    ]
    files += [(a.corpus / "invoices" / i["filename"], "invoice") for i in gt["invoices"]]
    async with httpx.AsyncClient(base_url=a.api, timeout=60) as c:
        h = await _auth(c, a.email, a.invite_code)
        sem = asyncio.Semaphore(8)
        await asyncio.gather(*(_upload(c, h, sem, p, k) for p, k in files))
        print(f"uploaded {len(files)} files; waiting for the worker")
        while True:
            counts = await _statuses(c, h)
            print("  " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
            if not counts.get("pending") and not counts.get("processing"):
                break
            await asyncio.sleep(5)
        if counts.get("failed"):
            print("some documents failed; check `GET /documents` for their error field")
            return 1
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--api", default="http://localhost:8000")
    ap.add_argument("--email", default=os.environ.get("EVAL_EMAIL", "eval@example.com"))
    ap.add_argument("--invite-code", default=os.environ.get("EVAL_INVITE_CODE", ""))
    ap.add_argument("--corpus", type=Path, default=ROOT / "evals" / "corpus")
    ap.add_argument("--ground-truth", type=Path, default=ROOT / "evals" / "ground_truth.json")
    args = ap.parse_args()
    if not _is_local(args.api) and PASSWORD == "eval-local-only-password":
        sys.exit("Refusing the default password against a non-local API: set a strong EVAL_PASSWORD")
    sys.exit(asyncio.run(_main(args)))


if __name__ == "__main__":
    main()
