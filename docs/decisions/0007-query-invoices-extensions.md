# 0007: query_invoices takes several vendors and can group by vendor
- **Context:** SPEC §6.5 gives `query_invoices(vendor?, date_from?, date_to?, aggregate, limit)`. A multi-hop question ("which net-45 vendor billed the most in March?") needs one total per vendor, and the agent has at most 6 steps and a tiny free-tier call budget.
- **Decision:** add `vendors` (up to 10) and `group_by_vendor`. Sums are always per currency. Only invoices with `needs_review = false` are counted (ADR 0003). The model supplies values only: argument models forbid unknown fields, so an injected `org_id` is rejected, and the real org_id comes from the caller's token.
- **Why:** one exact SQL call instead of N calls plus arithmetic by the model, which would be both slower and wrong more often.
- **Limit:** vendor names match by case-insensitive substring (LIKE wildcards escaped), so "Acme" also matches "Acme Labs". Fine for this corpus, needs a vendor table for real data.
