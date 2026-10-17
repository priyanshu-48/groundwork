"""Compare the structured tables (invoices, contracts) to the synthetic ground truth, field by
field. Free: reads the database only, no API calls.

Run (from backend/, stack up and both backfills done):
    DATABASE_URL=postgresql+asyncpg://groundwork:groundwork@localhost:5433/groundwork \
        uv run python ../evals/check_extraction.py
"""

import argparse
import asyncio
import json
import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "backend"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sqlalchemy import text  # noqa: E402

from app.config import get_settings  # noqa: E402
from app.db import make_engine  # noqa: E402


def _d(x: object) -> Decimal | None:
    return None if x is None else Decimal(str(x))


def score_invoices(gt: dict, rows: list[dict]) -> dict[str, tuple[int, int]]:
    by = {i["invoice_number"]: i for i in gt["invoices"]}
    out: dict[str, list[int]] = {
        k: [0, 0]
        for k in ("vendor", "issue_date", "due_date", "currency", "total", "subtotal", "tax")
    }
    for r in rows:
        g = by.get(r["invoice_number"])
        if g is None or r["needs_review"]:
            continue
        checks = {
            "vendor": r["vendor"] == g["vendor"],
            "issue_date": str(r["issue_date"]) == g["issue_date"],
            "due_date": r["due_date"] is None or str(r["due_date"]) == g["due_date"],
            "currency": r["currency"] == g["currency"],
            "total": _d(r["total"]) == Decimal(g["total"]),
            "subtotal": _d(r["subtotal"]) == Decimal(g["subtotal"]),
            "tax": (_d(r["tax"]) or Decimal(0)) == Decimal(g["tax"]),
        }
        for k, ok in checks.items():
            out[k][0] += ok
            out[k][1] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


def score_contracts(gt: dict, rows: list[dict]) -> dict[str, tuple[int, int]]:
    by = {v["name"]: v["contract"]["facts"] for v in gt["vendors"]}
    out: dict[str, list[int]] = {
        k: [0, 0]
        for k in (
            "vendor",
            "payment_terms",
            "late_fee",
            "termination_notice",
            "auto_renewal",
            "liability_cap",
            "governing_law",
        )
    }
    for r in rows:
        f = by.get(r["vendor"])
        out["vendor"][1] += 1
        if f is None or r["needs_review"]:
            continue
        out["vendor"][0] += 1
        cur, amount = f["liability_cap"]["value"].split()
        checks = {
            "payment_terms": r["payment_terms_days"]
            == int(f["payment_terms"]["value"].split("-")[1]),
            "late_fee": _d(r["late_fee_percent"]) == Decimal(f["late_fee"]["value"].rstrip("%")),
            "termination_notice": r["termination_notice_days"]
            == int(f["termination_notice"]["value"].split()[0]),
            "auto_renewal": r["auto_renewal"] is (f["auto_renewal"]["value"] == "yes"),
            "liability_cap": (r["liability_cap_currency"], _d(r["liability_cap_amount"]))
            == (cur, Decimal(amount.replace(",", ""))),
            "governing_law": r["governing_law"] == f["governing_law"]["value"],
        }
        for k, ok in checks.items():
            out[k][0] += ok
            out[k][1] += 1
    return {k: (v[0], v[1]) for k, v in out.items()}


def _print(title: str, scores: dict[str, tuple[int, int]]) -> None:
    print(f"\n{title}")
    for k, (ok, n) in scores.items():
        print(f"  {k:<20} {ok}/{n}" + ("" if ok == n else "   <-- check"))


async def _main(args: argparse.Namespace) -> None:
    gt = json.loads((ROOT / "evals" / "ground_truth.json").read_text(encoding="utf8"))
    engine = make_engine(get_settings().database_url)
    try:
        async with engine.connect() as c:
            org = (
                await c.execute(
                    text("SELECT org_id FROM users WHERE email = :e"), {"e": args.email}
                )
            ).scalar_one()
            inv = [
                dict(r)
                for r in (
                    await c.execute(text("SELECT * FROM invoices WHERE org_id = :o"), {"o": org})
                ).mappings()
            ]
            con = [
                dict(r)
                for r in (
                    await c.execute(text("SELECT * FROM contracts WHERE org_id = :o"), {"o": org})
                ).mappings()
            ]
    finally:
        await engine.dispose()
    flagged_i = sum(1 for r in inv if r["needs_review"])
    flagged_c = sum(1 for r in con if r["needs_review"])
    print(
        f"invoices: {len(inv)} rows ({flagged_i} flagged); contracts: {len(con)} rows ({flagged_c} flagged)"
    )
    _print("invoice fields correct (clean rows only)", score_invoices(gt, inv))
    _print("contract fields correct (clean rows only)", score_contracts(gt, con))


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--email", default="eval@example.com")
    asyncio.run(_main(ap.parse_args()))


if __name__ == "__main__":
    main()
