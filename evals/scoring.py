"""Decide whether an agent's free-text answer is right, and whether its citations are relevant.

Deliberately simple and rule-based (no LLM judge, so scoring is free, deterministic and cannot
share the model's blind spots). Known limits are listed in docs/decisions/0008-answer-scoring.md."""

import re
from datetime import date
from decimal import Decimal, InvalidOperation
from typing import Any

from evals.generate_corpus import GOVERNING_LAW

_ISO_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_INVOICE_NO = re.compile(r"\bV\d{2}-2025-\d{4}\b")
_NUMBER = re.compile(r"-?\d[\d,]*(?:\.\d+)?")


def norm(s: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s.lower()).split())


def numbers(text: str) -> list[Decimal]:
    """Numbers in an answer, ignoring dates and invoice numbers (their digits are not amounts)."""
    text = _INVOICE_NO.sub(" ", _ISO_DATE.sub(" ", text))
    out: list[Decimal] = []
    for tok in _NUMBER.findall(text):
        try:
            out.append(Decimal(tok.replace(",", "")))
        except InvalidOperation:
            continue
    return out


def _ints_in(text: str, allowed: set[int]) -> set[int]:
    return {int(n) for n in numbers(text) if n == int(n) and int(n) in allowed}


def _auto_renewal(answer: str) -> str | None:
    a = answer.lower()
    if re.search(
        r"(does not|doesn'?t|do not|will not|not)\s+(automatically\s+)?renew|no automatic|non-?renew|expires",
        a,
    ):
        return "no"
    if re.search(
        r"renews?\s+automatically|automatic(ally)?\s+renew|auto-?renew", a
    ) or a.startswith("yes"):
        return "yes"
    return "no" if a.startswith("no") else None


def score_contract(fact: str, gold: str, answer: str) -> bool:
    if fact == "payment_terms":
        return _ints_in(answer, {15, 30, 45, 60}) == {int(gold.split("-")[1])}
    if fact == "termination_notice":
        return _ints_in(answer, {30, 45, 60, 90, 120}) == {int(gold.split()[0])}
    if fact == "late_fee":
        found = {
            Decimal(m)
            for m in re.findall(r"(\d+(?:\.\d+)?)\s*(?:%|percent|per cent)", answer.lower())
        }
        return found == {Decimal(gold.rstrip("%"))}
    if fact == "auto_renewal":
        return _auto_renewal(answer) == gold
    if fact == "liability_cap":
        amounts = {int(n) for n in numbers(answer) if n >= 10_000 and n == int(n)}
        return amounts == {int(gold.split()[1].replace(",", ""))}
    if fact == "governing_law":
        a = norm(answer)
        key = lambda law: norm(law.replace("State of ", ""))  # noqa: E731
        others = [key(x) for x in GOVERNING_LAW if x != gold]
        return key(gold) in a and not any(o in a for o in others if o not in key(gold))
    raise ValueError(f"unknown fact {fact!r}")


def score_answer(q: dict[str, Any], answer: str, vendor_names: list[str]) -> bool:
    kind, atype = q["type"], q["answer_type"]
    if kind == "contract_lookup":
        return score_contract(q["fact"], q["answer"], answer)
    if atype == "decimal":
        return Decimal(q["answer"]) in numbers(answer)
    if atype == "int":
        return Decimal(q["answer"]) in numbers(answer)
    if atype == "list":
        return set(_INVOICE_NO.findall(answer)) == set(q["answer"])
    if atype == "text":  # multi-hop: the vendor, and only that vendor
        a = norm(answer)
        others = [norm(v) for v in vendor_names if v != q["answer"]]
        return norm(q["answer"]) in a and not any(o in a for o in others)
    raise ValueError(f"cannot score {kind}/{atype}")


def citation_counts(
    q: dict[str, Any], citations: list[dict[str, Any]], gt: dict[str, Any]
) -> tuple[int, int] | None:
    """(relevant, total) cited chunks, or None when precision is not defined for this question.

    Relevant means the chunk is from a document that actually holds the answer: for a contract
    lookup the gold document AND page, for an invoice aggregate any invoice of that vendor in the
    asked date range. Multi-hop answers span many documents, so they are not scored here."""
    if q["type"] == "contract_lookup":
        g = q["gold"]
        rel = sum(1 for c in citations if c["filename"] == g["document"] and c["page"] == g["page"])
        return rel, len(citations)
    if q["type"] == "invoice_aggregate":
        lo, hi = date.fromisoformat(q["date_from"]), date.fromisoformat(q["date_to"])
        files = {
            i["filename"]
            for i in gt["invoices"]
            if i["vendor"] == q["vendor"] and lo <= date.fromisoformat(i["issue_date"]) <= hi
        }
        return sum(1 for c in citations if c["filename"] in files), len(citations)
    return None
