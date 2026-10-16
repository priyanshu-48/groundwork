# 0003: Flag doubtful invoices instead of failing or trusting them
- **Context:** SPEC §5 has UNIQUE(org_id, vendor, invoice_number); §6.3 says failed validation must be marked for review, not stored silently.
- **Decision:** Invoice rows carry `needs_review` + `review_reason`. The unique index is partial (`WHERE NOT needs_review`). Inconsistent totals, missing fields, and duplicate vendor+number are stored flagged; the document still becomes `ready`.
- **Why:** A plain UNIQUE would make a duplicate upload fail the whole ingest job forever. Flagged rows keep the evidence for a human without polluting numbers.
- **Consequence:** M6's `query_invoices` MUST filter `needs_review = false`.
