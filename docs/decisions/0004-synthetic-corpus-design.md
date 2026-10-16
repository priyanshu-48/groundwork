# 0004: Synthetic corpus design for evals
- **Context:** SPEC §7 wants a corpus with known answers so accuracy numbers are real.
- **Decision:** Gold pages are known by construction (each fact is assigned a page, the PDF is rendered with one page per section, then re-read with PyMuPDF to assert the text is on that page). Seeded, byte-deterministic PDFs. The 5 non-USD vendors only get net-15/net-60, so "net-30/net-45 vendors" comparisons are single-currency.
- **Metrics:** retrieval hit = right contract AND right page, on the 35 contract-lookup questions; document-level recall is reported as the looser number. Fake-embedder numbers never enter docs/evals.md.
- **Limits:** Templated clause wording is easier than real contracts, the corpus is small, and the question phrasing is ours. Treat results as a regression benchmark, not a claim about real-world accuracy.
