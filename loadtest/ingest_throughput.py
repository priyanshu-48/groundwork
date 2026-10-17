"""Ingestion throughput: upload N generated PDFs, wait until all are ready, report pages/min for
one worker. Run the stack with AI_PROVIDER=fake so the number is the pipeline's own ceiling
(parse, chunk, fake-embed, write); real throughput is bounded by Gemini quota instead.

Run (from backend/, stack up):  uv run python ../loadtest/ingest_throughput.py --n 60
Uses a fresh throwaway org, so any corpus already loaded is untouched."""

import argparse
import sys
import time
import uuid
from typing import Any

import httpx
import pymupdf

PW = "ingest-throughput-password"


def make_pdf(i: int, pages: int) -> bytes:
    doc = pymupdf.open()
    for p in range(pages):
        page = doc.new_page()
        words = " ".join(f"term{(i * 31 + p * 7 + j) % 997}" for j in range(450))
        page.insert_textbox(pymupdf.Rect(36, 36, 559, 806), f"Document {i} page {p + 1}. {words}", fontsize=8)
    return bytes(doc.tobytes())


def list_all(c: httpx.Client, h: dict[str, str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    while True:
        page = c.get("/documents", headers=h, params={"limit": 100, "offset": len(out)}).json()
        out += page
        if len(page) < 100:
            return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--pages", type=int, default=3)
    a = ap.parse_args()
    email = f"ingest-{uuid.uuid4().hex[:8]}@example.com"
    with httpx.Client(base_url=a.base, timeout=60) as c:
        r = c.post("/auth/signup", json={"org_name": "ingest", "email": email, "password": PW})
        r.raise_for_status()
        h = {"Authorization": f"Bearer {r.json()['access_token']}"}
        start = time.perf_counter()
        for i in range(a.n):
            files = {"file": (f"t{i}.pdf", make_pdf(i, a.pages), "application/pdf")}
            c.post("/documents", headers=h, data={"kind": "other"}, files=files).raise_for_status()
        uploaded = time.perf_counter() - start
        while True:
            docs = list_all(c, h)
            if len(docs) == a.n and all(d["status"] in ("ready", "failed") for d in docs):
                break
            time.sleep(1)
        total = time.perf_counter() - start
    ready = sum(1 for d in docs if d["status"] == "ready")
    pages = sum(d.get("page_count") or 0 for d in docs if d["status"] == "ready")
    print(f"ready {ready}/{a.n}  pages {pages}  upload {uploaded:.1f}s  total {total:.1f}s")
    print(f"throughput: {ready / total * 60:.0f} docs/min, {pages / total * 60:.0f} pages/min")
    return 0 if ready == a.n else 1


if __name__ == "__main__":
    sys.exit(main())
