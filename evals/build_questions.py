"""Turn ground_truth.json into questions.jsonl: ~90 questions with known answers.

Run (from backend/):  uv run python ../evals/build_questions.py
"""

import argparse
import calendar
import json
import random
from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Any

FACTS = [
    "payment_terms",
    "late_fee",
    "termination_notice",
    "auto_renewal",
    "liability_cap",
    "governing_law",
]
LOOKUP_WORDING = {
    "payment_terms": "What are the payment terms in the {v} contract?",
    "late_fee": "What is the late-payment penalty in the {v} contract?",
    "termination_notice": "What is the termination notice period in the {v} contract?",
    "auto_renewal": "Does the {v} contract renew automatically?",
    "liability_cap": "What is the liability cap in the {v} contract?",
    "governing_law": "Which law governs the {v} contract?",
}


def _lookups(gt: dict[str, Any], rng: random.Random, n: int) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    base, extra = divmod(n, len(FACTS))
    for i, fact in enumerate(FACTS):
        k = min(base + (1 if i < extra else 0), len(gt["vendors"]))
        for v in rng.sample(gt["vendors"], k):
            f = v["contract"]["facts"][fact]
            out.append(
                {
                    "type": "contract_lookup",
                    "fact": fact,
                    "vendor": v["name"],
                    "question": LOOKUP_WORDING[fact].format(v=v["name"]),
                    "answer": f["value"],
                    "answer_type": "text",
                    "gold": {"document": v["contract"]["filename"], "page": f["page"]},
                }
            )
    rng.shuffle(out)
    return out


def _in_range(inv: dict[str, Any], lo: date, hi: date) -> bool:
    return lo <= date.fromisoformat(inv["issue_date"]) <= hi


def _random_range(rng: random.Random) -> tuple[date, date]:
    kind = rng.choice(["month", "quarter", "two_months"])
    first = rng.randint(1, 12)
    span = {"month": 1, "quarter": 3, "two_months": 2}[kind]
    if kind == "quarter":
        first = rng.choice([1, 4, 7, 10])
    last = min(first + span - 1, 12)
    return date(2025, first, 1), date(2025, last, calendar.monthrange(2025, last)[1])


def _aggregates(gt: dict[str, Any], rng: random.Random, n: int) -> list[dict[str, Any]]:
    n_count, n_list = round(n * 10 / 35), round(n * 10 / 35)
    kinds = ["count"] * n_count + ["list"] * n_list + ["sum"] * (n - n_count - n_list)
    rng.shuffle(kinds)
    out: list[dict[str, Any]] = []
    seen: set[tuple[Any, ...]] = set()
    for agg in kinds:
        for _ in range(2000):
            v = rng.choice(gt["vendors"])
            lo, hi = _random_range(rng)
            rows = [i for i in gt["invoices"] if i["vendor_id"] == v["id"] and _in_range(i, lo, hi)]
            key = (agg, v["id"], lo, hi)
            if not rows or key in seen or (agg == "list" and len(rows) > 10):
                continue
            seen.add(key)
            q: dict[str, Any] = {
                "type": "invoice_aggregate",
                "aggregate": agg,
                "vendor": v["name"],
                "date_from": lo.isoformat(),
                "date_to": hi.isoformat(),
                "gold": None,
            }
            if agg == "sum":
                q |= {
                    "question": f"How much did {v['name']} bill us between {lo} and {hi}?",
                    "answer": str(sum((Decimal(r["total"]) for r in rows), Decimal(0))),
                    "answer_type": "decimal",
                    "currency": v["currency"],
                }
            elif agg == "count":
                q |= {
                    "question": f"How many invoices did {v['name']} issue between {lo} and {hi}?",
                    "answer": len(rows),
                    "answer_type": "int",
                }
            else:
                q |= {
                    "question": f"List the invoice numbers {v['name']} issued between {lo} and {hi}.",
                    "answer": sorted(r["invoice_number"] for r in rows),
                    "answer_type": "list",
                }
            out.append(q)
            break
        else:
            raise RuntimeError(f"could not build a valid {agg} question")
    return out


def _multi_hop(gt: dict[str, Any], rng: random.Random, n: int) -> list[dict[str, Any]]:
    """Only net-30/net-45 vendors, which are all USD by construction, so totals are comparable."""
    terms_of = {v["name"]: v["contract"]["facts"]["payment_terms"]["value"] for v in gt["vendors"]}
    cur_of = {v["name"]: v["currency"] for v in gt["vendors"]}
    cands = [(t, m) for t in ("net-30", "net-45") for m in range(1, 13)]
    rng.shuffle(cands)
    n_max = round(n * 0.6)
    out: list[dict[str, Any]] = []
    for terms, month in cands:
        if len(out) == n:
            break
        totals: dict[str, Decimal] = {}
        for i in gt["invoices"]:
            if terms_of[i["vendor"]] == terms and i["issue_date"].startswith(f"2025-{month:02d}"):
                totals[i["vendor"]] = totals.get(i["vendor"], Decimal(0)) + Decimal(i["total"])
        if not totals:
            continue
        assert {cur_of[v] for v in totals} == {"USD"}
        name = f"{calendar.month_name[month]} 2025"
        base = {"type": "multi_hop", "terms": terms, "month": f"2025-{month:02d}", "gold": None}
        if len([q for q in out if q["answer_type"] == "text"]) < n_max:
            best = max(totals.values())
            winners = [v for v, t in totals.items() if t == best]
            if len(totals) < 2 or len(winners) != 1:
                continue
            out.append(
                base
                | {
                    "question": f"Which vendor on {terms} terms billed us the most in {name}?",
                    "answer": winners[0],
                    "answer_type": "text",
                }
            )
        else:
            out.append(
                base
                | {
                    "question": f"What is the total billed by {terms} vendors in {name}?",
                    "answer": str(sum(totals.values(), Decimal(0))),
                    "answer_type": "decimal",
                    "currency": "USD",
                }
            )
    if len(out) < n:
        raise RuntimeError(f"only {len(out)} valid multi-hop questions, wanted {n}")
    return out


def build_questions(
    gt: dict[str, Any],
    seed: int = 42,
    n_lookup: int = 35,
    n_aggregate: int = 35,
    n_hop: int = 20,
) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    qs = (
        _lookups(gt, rng, n_lookup) + _aggregates(gt, rng, n_aggregate) + _multi_hop(gt, rng, n_hop)
    )
    prefix = {"contract_lookup": "c", "invoice_aggregate": "a", "multi_hop": "m"}
    counters: dict[str, int] = {}
    for q in qs:
        counters[q["type"]] = counters.get(q["type"], 0) + 1
        q["id"] = f"{prefix[q['type']]}{counters[q['type']]:02d}"
    return qs


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ground-truth", type=Path, default=root / "evals" / "ground_truth.json")
    ap.add_argument("--out", type=Path, default=root / "evals" / "questions.jsonl")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    qs = build_questions(json.loads(a.ground_truth.read_text(encoding="utf8")), a.seed)
    a.out.write_text("\n".join(json.dumps(q, sort_keys=True) for q in qs) + "\n", encoding="utf8")
    print(f"wrote {len(qs)} questions to {a.out}")


if __name__ == "__main__":
    main()
