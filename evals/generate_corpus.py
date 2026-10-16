"""Deterministic synthetic corpus: vendor contracts and invoices with known ground truth.

Why synthetic: every fact and its page is known by construction, so evals report real accuracy
instead of "it seems to work". The same seed always yields the same ground truth and the same
PDF bytes. See docs/decisions/0004-synthetic-corpus-design.md.

Run (from backend/):  uv run python ../evals/generate_corpus.py
"""

import argparse
import json
import random
import re
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path
from typing import Any

import pymupdf
from faker import Faker
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

CLIENT = "Northfield Holdings"
PREFIXES = [
    "Northwind", "Bluepeak", "Ironbridge", "Silverline", "Redwood", "Clearwater", "Stonegate",
    "Brightside", "Harborview", "Maplecrest", "Oakridge", "Summit", "Lakeshore", "Pinnacle",
    "Evergreen", "Crestline", "Falcon", "Granite", "Horizon", "Juniper", "Kestrel", "Lumen",
    "Meridian", "Nimbus", "Orchard", "Prairie", "Quarry", "Ridgeway", "Sterling", "Tidewater",
]  # fmt: skip
SUFFIXES = [
    "Logistics", "Software", "Consulting", "Supplies", "Analytics", "Cloud", "Staffing", "Print",
    "Energy", "Security", "Labs", "Foods", "Media", "Telecom", "Facilities",
]  # fmt: skip
GOVERNING_LAW = [
    "State of Delaware", "State of New York", "State of California", "State of Texas",
    "State of Washington", "England and Wales",
]  # fmt: skip
SERVICES = [
    "Monthly service fee", "Implementation work", "Support hours", "Licence renewal",
    "Freight and handling", "Consulting day rate", "Equipment rental", "Training session",
    "Storage fees", "Software subscription", "Maintenance visit", "Data transfer",
]  # fmt: skip
DAY_WORDS = {
    15: "fifteen", 30: "thirty", 45: "forty-five", 60: "sixty", 90: "ninety", 120: "one hundred twenty",
}  # fmt: skip
FACTS = [
    "payment_terms",
    "late_fee",
    "termination_notice",
    "auto_renewal",
    "liability_cap",
    "governing_law",
]
FILLERS = [
    ("Confidentiality", "Each party shall keep the other party's confidential information secret and use it only to perform this Agreement. This obligation continues for {years} years after the Agreement ends."),
    ("Intellectual Property", "Each party keeps ownership of the intellectual property it brought to the relationship. Work product created specifically for the Client is licensed to the Client on a perpetual basis."),
    ("Warranties", "The Supplier warrants that the services will be performed with reasonable skill and care by suitably qualified personnel and in accordance with applicable law."),
    ("Indemnification", "The Supplier shall defend the Client against third-party claims that the services infringe intellectual property rights, provided the Client gives prompt written notice of the claim."),
    ("Force Majeure", "Neither party is liable for delay caused by events beyond its reasonable control, including natural disasters, strikes, or failures of public utilities, provided it notifies the other party promptly."),
    ("Assignment", "Neither party may assign this Agreement without the prior written consent of the other party, which shall not be unreasonably withheld, except to a successor in a merger."),
    ("Notices", "Notices under this Agreement must be in writing and delivered to the attention of {name} at {address} or to any other address a party designates by notice."),
    ("Entire Agreement", "This Agreement is the entire understanding between the parties on its subject matter and replaces all earlier proposals, discussions, and understandings."),
    ("Severability", "If any provision is found unenforceable, the remaining provisions continue in full effect and the unenforceable provision is limited to the minimum extent necessary."),
    ("Data Protection", "Each party shall comply with applicable data protection law and process personal data only as needed to perform this Agreement, using appropriate security measures."),
    ("Insurance", "The Supplier shall maintain commercial insurance with a reputable carrier throughout the term and provide a certificate of insurance on request."),
    ("Audit Rights", "The Client may, on {days} days' notice and no more than once a year, audit the Supplier's records relating to charges made under this Agreement."),
    ("Subcontractors", "The Supplier remains responsible for the acts of its subcontractors and shall not engage a subcontractor to perform core services without the Client's approval."),
    ("Dispute Resolution", "The parties shall first try to resolve any dispute through good-faith discussion between senior managers before starting formal proceedings."),
]  # fmt: skip


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _money(d: Decimal) -> str:
    return f"{d:,.2f}"


def _q(d: Decimal) -> Decimal:
    return d.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _facts(rng: random.Random, currency: str) -> dict[str, dict[str, Any]]:
    terms = rng.choice(
        ["net-15", "net-60"] if currency != "USD" else ["net-15", "net-30", "net-45", "net-60"]
    )
    days = int(terms.split("-")[1])
    fee = rng.choice(["0.5%", "1.0%", "1.5%", "2.0%", "3.0%"])
    notice = rng.choice([30, 45, 60, 90, 120])
    renew = rng.choice(["yes", "no"])
    cap = f"{currency} {rng.choice([50_000, 100_000, 250_000, 500_000, 1_000_000]):,}"
    law = rng.choice(GOVERNING_LAW)
    renewal_text = (
        "Term and Renewal. This Agreement renews automatically for successive one-year terms unless either party gives written notice of non-renewal before the end of the current term."
        if renew == "yes"
        else "Term and Renewal. This Agreement expires at the end of its initial term and does not renew automatically unless the parties sign a written extension."
    )
    return {
        "payment_terms": {
            "value": terms,
            "text": f"Payment Terms. {CLIENT} shall pay each undisputed invoice within {DAY_WORDS[days]} ({days}) days of the invoice date ({terms.replace('-', ' ').title()}).",
        },
        "late_fee": {
            "value": fee,
            "text": f"Late Payment. Any undisputed amount not paid when due accrues a late fee of {fee} per month until it is paid in full.",
        },
        "termination_notice": {
            "value": f"{notice} days",
            "text": f"Termination for Convenience. Either party may terminate this Agreement for any reason by giving {DAY_WORDS[notice]} ({notice}) days' written notice to the other party.",
        },
        "auto_renewal": {"value": renew, "text": renewal_text},
        "liability_cap": {
            "value": cap,
            "text": f"Limitation of Liability. The total aggregate liability of either party arising out of this Agreement shall not exceed {cap}.",
        },
        "governing_law": {
            "value": law,
            "text": f"Governing Law. This Agreement is governed by the laws of the {law}, without regard to its conflict-of-law principles.",
        },
    }


def build_ground_truth(
    seed: int = 42, n_vendors: int = 25, n_invoices: int = 300
) -> dict[str, Any]:
    """Pure data, no files: vendors with contract facts (and their pages), and invoices."""
    rng = random.Random(seed)
    names = rng.sample(PREFIXES, n_vendors)
    n_foreign = max(1, round(n_vendors * 0.2))
    foreign = set(rng.sample(range(n_vendors), n_foreign))
    vendors: list[dict[str, Any]] = []
    for i, prefix in enumerate(names, start=1):
        name = f"{prefix} {rng.choice(SUFFIXES)}"
        currency = ["EUR", "GBP"][i % 2] if (i - 1) in foreign else "USD"
        pages = rng.randint(3, 6)
        facts = _facts(rng, currency)
        for f in facts.values():
            f["page"] = rng.randint(1, pages)
        vendors.append(
            {
                "id": i,
                "name": name,
                "currency": currency,
                "tax_rate": str(rng.choice(["0", "0", "0.05", "0.10", "0.18"])),
                "scale": rng.choice([1, 2, 3, 5, 8, 13]),
                "contract": {
                    "filename": f"contract_{i:02d}_{_slug(name)}.pdf",
                    "pages": pages,
                    "facts": facts,
                },
            }
        )

    invoices: list[dict[str, Any]] = []
    counts = {v["id"]: 0 for v in vendors}
    for n in range(n_invoices):
        v = vendors[n % n_vendors]
        counts[v["id"]] += 1
        number = f"V{v['id']:02d}-2025-{counts[v['id']]:04d}"
        issue = date(2025, 1, 1) + timedelta(days=rng.randrange(365))
        days = int(v["contract"]["facts"]["payment_terms"]["value"].split("-")[1])
        lines = []
        for _ in range(rng.randint(2, 5)):
            qty = rng.randint(1, 20)
            unit = _q(Decimal(rng.randint(500, 20_000)) / 100 * v["scale"])
            lines.append(
                {
                    "description": rng.choice(SERVICES),
                    "qty": qty,
                    "unit_price": str(unit),
                    "amount": str(_q(unit * qty)),
                }
            )
        subtotal = sum((Decimal(line["amount"]) for line in lines), Decimal(0))
        tax = _q(subtotal * Decimal(v["tax_rate"]))
        invoices.append(
            {
                "filename": f"invoice_{number}.pdf",
                "vendor_id": v["id"],
                "vendor": v["name"],
                "invoice_number": number,
                "issue_date": issue.isoformat(),
                "due_date": (issue + timedelta(days=days)).isoformat(),
                "currency": v["currency"],
                "lines": lines,
                "subtotal": str(subtotal),
                "tax": str(tax),
                "total": str(subtotal + tax),
                "template": rng.randrange(3),
            }
        )
    return {"seed": seed, "client": CLIENT, "vendors": vendors, "invoices": invoices}


# ---------------------------------------------------------------- rendering

_BASE = getSampleStyleSheet()
BODY = ParagraphStyle("body", parent=_BASE["BodyText"], fontSize=10, leading=14, spaceAfter=8)
TITLE = ParagraphStyle("title", parent=_BASE["Title"], fontSize=16, spaceAfter=10)


def _doc(path: Path) -> SimpleDocTemplate:
    return SimpleDocTemplate(str(path), pagesize=A4, invariant=1, topMargin=50, bottomMargin=40)


def _render_contract(v: dict[str, Any], path: Path, seed: int) -> None:
    rng = random.Random(f"{seed}-contract-{v['id']}")
    fake = Faker("en_US")
    fake.seed_instance(seed * 1000 + v["id"])
    pages = v["contract"]["pages"]
    by_page: dict[int, list[str]] = {p: [] for p in range(1, pages + 1)}
    for f in v["contract"]["facts"].values():
        by_page[f["page"]].append(f["text"])
    fillers = list(FILLERS)
    rng.shuffle(fillers)
    section = 0
    story: list[Any] = [Paragraph("MASTER SERVICES AGREEMENT", TITLE)]
    for p in range(1, pages + 1):
        paras = list(by_page[p])
        want = 5 if p > 1 else 4
        while len(paras) < want:
            title, tmpl = fillers.pop() if fillers else rng.choice(FILLERS)
            paras.append(
                f"{title}. "
                + tmpl.format(
                    years=rng.choice([2, 3, 5]),
                    name=fake.name(),
                    address=fake.address().replace("\n", ", "),
                    days=rng.choice([10, 15, 30]),
                )
            )
        rng.shuffle(paras)
        if p == 1:
            story.append(
                Paragraph(
                    f"This Master Services Agreement is made on {fake.date_object().replace(year=2024).isoformat()} "
                    f"between {v['name']} (the Supplier), of {fake.address().replace(chr(10), ', ')}, "
                    f"and {CLIENT} (the Client).",
                    BODY,
                )
            )
        for text in paras:
            section += 1
            story.append(Paragraph(f"Section {section}. {text}", BODY))
        if p < pages:
            story.append(PageBreak())

    def header(canvas: Any, doc: Any) -> None:
        canvas.setFont("Helvetica", 8)
        canvas.drawString(50, 812, f"{v['name']} - Master Services Agreement - Page {doc.page}")

    _doc(path).build(story, onFirstPage=header, onLaterPages=header)


def _render_invoice(inv: dict[str, Any], v: dict[str, Any], path: Path, seed: int) -> None:
    fake = Faker("en_US")
    fake.seed_instance(seed * 7919 + v["id"])
    cur = inv["currency"]
    terms = v["contract"]["facts"]["payment_terms"]["value"]
    has_tax = Decimal(inv["tax"]) > 0
    rate_pct = f"{Decimal(v['tax_rate']) * 100:.0f}%"
    rows = [["Description", "Qty", "Unit price", "Amount"]] + [
        [
            ln["description"],
            str(ln["qty"]),
            _money(Decimal(ln["unit_price"])),
            _money(Decimal(ln["amount"])),
        ]
        for ln in inv["lines"]
    ]
    table = Table(rows, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [("GRID", (0, 0), (-1, -1), 0.4, colors.grey), ("FONTSIZE", (0, 0), (-1, -1), 9)]
        )
    )
    sub, tax, tot = (_money(Decimal(inv[k])) for k in ("subtotal", "tax", "total"))
    bill_to = f"{CLIENT}, {fake.address().replace(chr(10), ', ')}"
    story: list[Any]
    if inv["template"] == 0:  # labelled lines
        story = [Paragraph("INVOICE", TITLE)]
        for label, value in [
            ("Vendor", inv["vendor"]), ("Invoice #", inv["invoice_number"]),
            ("Issue Date", inv["issue_date"]), ("Due Date", inv["due_date"]),
            ("Currency", cur), ("Bill To", bill_to),
        ]:  # fmt: skip
            story.append(Paragraph(f"{label}: {value}", BODY))
        story += [table, Spacer(1, 10), Paragraph(f"Subtotal: {sub}", BODY)]
        if has_tax:
            story.append(Paragraph(f"Tax: {tax}", BODY))
        story += [Paragraph(f"Total: {tot}", BODY), Paragraph(f"Payment terms: {terms}", BODY)]
    elif inv["template"] == 1:  # letterhead style
        story = [
            Paragraph(inv["vendor"], TITLE),
            Paragraph("TAX INVOICE", BODY),
            Paragraph(f"Invoice No. {inv['invoice_number']}", BODY),
            Paragraph(f"Date of issue: {inv['issue_date']}", BODY),
            Paragraph(f"Payment due: {inv['due_date']}", BODY),
            Paragraph(f"Billed to: {bill_to}", BODY),
            table,
            Spacer(1, 10),
            Paragraph(f"Sub-total ({cur}): {sub}", BODY),
        ]
        if has_tax:
            story.append(Paragraph(f"VAT/GST ({rate_pct}): {tax}", BODY))
        story.append(Paragraph(f"Amount due ({cur}): {tot}", BODY))
    else:  # compact
        story = [
            Paragraph(f"{inv['vendor']} | Ref {inv['invoice_number']}", TITLE),
            Paragraph(f"Issued {inv['issue_date']} - due {inv['due_date']} - {cur}", BODY),
            table,
            Spacer(1, 10),
            Paragraph(
                f"Net {sub}" + (f" + tax {tax}" if has_tax else "") + f" = TOTAL {cur} {tot}", BODY
            ),
            Paragraph(f"Customer: {bill_to}", BODY),
        ]
    _doc(path).build(story)


def render_corpus(gt: dict[str, Any], out: Path, seed: int = 42, verify: bool = True) -> None:
    (out / "contracts").mkdir(parents=True, exist_ok=True)
    (out / "invoices").mkdir(parents=True, exist_ok=True)
    by_id = {v["id"]: v for v in gt["vendors"]}
    for v in gt["vendors"]:
        _render_contract(v, out / "contracts" / v["contract"]["filename"], seed)
    for inv in gt["invoices"]:
        _render_invoice(inv, by_id[inv["vendor_id"]], out / "invoices" / inv["filename"], seed)
    if verify:
        verify_corpus(gt, out)


def _norm(s: str) -> str:
    return " ".join(s.split())


def verify_corpus(gt: dict[str, Any], out: Path) -> None:
    """Re-read every PDF and check the ground truth really is where we say it is."""
    for v in gt["vendors"]:
        with pymupdf.open(out / "contracts" / v["contract"]["filename"]) as doc:
            assert doc.page_count == v["contract"]["pages"], f"{v['name']}: page overflow"
            for kind, fact in v["contract"]["facts"].items():
                page_text = _norm(doc[fact["page"] - 1].get_text())
                assert _norm(fact["text"]) in page_text, (
                    f"{v['name']} {kind} not on page {fact['page']}"
                )
                assert v["name"] in page_text
    for inv in gt["invoices"]:
        with pymupdf.open(out / "invoices" / inv["filename"]) as doc:
            text = _norm(doc[0].get_text())
        assert inv["invoice_number"] in text and _money(Decimal(inv["total"])) in text, inv[
            "filename"
        ]


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", type=Path, default=root / "evals" / "corpus")
    ap.add_argument("--ground-truth", type=Path, default=root / "evals" / "ground_truth.json")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--vendors", type=int, default=25)
    ap.add_argument("--invoices", type=int, default=300)
    a = ap.parse_args()
    gt = build_ground_truth(a.seed, a.vendors, a.invoices)
    render_corpus(gt, a.out, a.seed)
    a.ground_truth.write_text(json.dumps(gt, indent=2, sort_keys=True) + "\n", encoding="utf8")
    print(f"wrote {len(gt['vendors'])} contracts and {len(gt['invoices'])} invoices to {a.out}")


if __name__ == "__main__":
    main()
