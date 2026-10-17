# Portfolio entry and resume bullets (measured numbers only)

Every number below comes from `docs/evals.md`, the test suite or the load tests, and is labelled with
what it was measured on. Do not round up, and do not add a number you did not measure.

## Project card (about 150 words)
**Groundwork: document Q&A agent with citations.** A multi-tenant web app where a user uploads
invoices and contracts and asks questions in plain language. A hand-written tool-calling agent (FastAPI,
Gemini) chooses between hybrid document search (pgvector + Postgres full-text, fused with RRF) and
parameterised SQL over extracted invoice and contract data, then answers with citations that open the
source page. Built end to end: crash-safe ingestion on a Postgres job queue, a React/TypeScript chat UI
with streamed answers, JSON logs and metrics, rate limiting, an evaluation harness over a synthetic
corpus with known answers, and a deployment on AWS with HTTPS and tested backups. A public read-only
demo workspace has a daily cap to protect a free API quota. Links: live demo, GitHub, README.

## Resume bullets
- Built a **tool-calling AI agent** (FastAPI, Gemini) that answers questions over invoices and contracts with **cited sources**, combining **hybrid retrieval** (pgvector + Postgres full-text, reciprocal rank fusion) with **parameterised SQL tools** for aggregates; **100% (90/90) correct** on a 90-question rule-scored evaluation over a synthetic corpus.
- Raised retrieval **recall@5 from 81.7% to 93.3%** on a 60-question hard set (exact invoice-number queries **50% to 100%**) by adding keyword search and rank fusion to vector search, measured with a custom harness; measured a cross-encoder reranker too, found it slower (about 1.4 s) and worse on this set, and left it off.
- Moved multi-hop questions ("which net-30 vendor billed the most in March?") from **30% to 100%** by extracting contract terms into structured tables instead of searching for them.
- Designed **crash-safe ingestion** on a Postgres `SKIP LOCKED` queue with idempotent uploads, retries with backoff and a stuck-job reaper; a fault-injection test shows a crash before commit leaves nothing and the re-run leaves **0 duplicate chunks**.
- Deployed to **AWS (EC2, S3) behind automatic HTTPS** with Docker Compose, secrets in Parameter Store, no SSH and no stored cloud keys; nightly backups with a **restore drill passed**; written so a move to Oracle Cloud needs config changes only.
- Load-tested with **k6**: search **p95 24 ms warm / 538 ms cold** at 20 req/s, 0 errors; **373 backend tests (93% line coverage)** including tenant-isolation and prompt-injection tests, plus 62 frontend tests and a Playwright end-to-end test.
- **Tech stack:** Python, FastAPI, PostgreSQL, pgvector, Gemini API, React, TypeScript, Docker, Caddy, AWS, pytest, Playwright, k6.

Notes on wording you may be asked about:
- "Evaluation set" means templated questions over a generated corpus, a regression benchmark, not accuracy on real documents. Say so if asked.
- CI is defined in `.github/workflows/ci.yml`. Add "GitHub Actions CI" only after the repository is on GitHub and the first run is green. Deploys are scripted, not automated (ADR 0015); do not write "CI/CD".
- There is no RDS or CloudFront (ADR 0014). Do not list them.

## Interview talking points (mapped to the questions in SPEC section 13)
1. **Hybrid search.** Why exact IDs fail on embeddings and what RRF does (fuse by rank, not score). Numbers: exact-ID recall 50% to 100%. [ADR 0005, docs/evals.md]
2. **When search is the wrong tool.** "List everything that matches" cannot come from top-k chunks; the 30% to 100% multi-hop change. [ADR 0010]
3. **Trusting model output.** Extraction is validated and doubtful rows are flagged, not trusted; money is `Decimal`; the model never writes SQL; document text is escaped before the model sees it. [ADR 0003, tests]
4. **Free-tier engineering.** Per-model quotas, fallback chain (never for embeddings), min-interval throttles, resumable cached evals, and a daily cap on the public demo. [ADR 0009, 0016]
5. **A reranker that did not help.** How the measurement was set up, why the easy set hid it, and why the default stayed hybrid. [docs/evals.md]
6. **Production lessons.** An empty environment variable crashed the API only on the real host; scripts lost their executable bit on Windows and the restore drill caught it. [journal]
