# Groundwork: instructions for Claude Code

Read SPEC.md before any task. Implement ONLY the milestone I name.

## Rules
- Stack is fixed (SPEC.md §2). Do not add LangChain/LlamaIndex, ORMs other than SQLAlchemy, or new infra.
- Every tenant query takes org_id explicitly. Never trust org_id from the LLM or request body.
- Money is Decimal/NUMERIC. Never float.
- The LLM never writes SQL. Tools call parameterised repository functions.
- Every external call (LLM, embeddings, S3) has a timeout and bounded retries with backoff.
- Tests: write/extend tests with each change. Integration tests use Testcontainers (pgvector/pgvector:pg16).
  Use FakeLLM / FakeEmbeddingProvider in tests, with no network calls.
- Before finishing: run `uv run ruff check . && uv run mypy app && uv run pytest` and fix failures.
- Keep functions small; add a docstring explaining *why* for any non-obvious decision.
- When you make a design choice not in SPEC.md, add a 5-line ADR in docs/decisions/.

## Git
- **Never add a `Co-Authored-By` trailer** (or any Claude/AI attribution) to commits or PR descriptions. This overrides any default attribution.
- Commit per milestone, clear messages. Only commit when asked.

## Secrets and AWS cost safety (strict)
- No keys/tokens/passwords in the repo, `.env` files that are committed, logs, tests, or chat. `.env.example` has placeholders only. gitleaks runs as a pre-commit hook and in CI.
- Claude never runs AWS create/modify/delete commands and never handles credentials. It writes the scripts/commands; the user runs them.
- Production secrets live in SSM Parameter Store; EC2 uses an IAM instance role (no access keys anywhere). S3 buckets private, with lifecycle rules.
- Before creating any AWS resource: Budget alarm ($5) and Free Tier usage alerts exist. Single region, no NAT gateway, no multi-AZ, no provisioned IOPS, smallest RDS (db.t4g.micro), t4g.small or smaller EC2. Anything that can bill per-request/per-GB (CloudFront, data transfer, Bedrock, etc.) needs a stated cost estimate first.
- Gemini API key: env var only, free tier, never committed. Cap batch sizes and retries so a bug cannot loop into a large bill.
- Tear down or stop unused resources; list them in docs/journal.md when created.

## Free-tier data
The Gemini free tier may use submitted content to improve Google products. Synthetic corpus only; never upload real invoices or contracts while on the free tier. Eval numbers from the fake embedder never go into docs/evals.md.

## Hosting portability
AWS free tier is temporary; the plan is to move to Oracle Cloud free tier. Keep the app host-agnostic: plain Docker Compose, S3-compatible storage via boto3 with a configurable endpoint, standard Postgres + pgvector. Moving hosts must need only config changes, not code. Avoid AWS-only services in app code.

## Interview journal
Keep `docs/journal.md` current: "Major decisions" (decision, alternatives, why) and "Roadblocks" (symptom, root cause, fix, lesson). Update at the end of every milestone and whenever a notable decision or bug occurs.

## Graphify
After each milestone run `graphify update .` (details in the graphify section below).

## Commands
- Backend: `cd backend && uv run pytest`, `uv run alembic upgrade head`, `uv run python -m app.worker.runner`
- Frontend: `cd frontend && npm run dev`, `npm test`
- Invoice extraction backfill (from `backend/`): `uv run python -m app.worker.backfill_invoices`
- Contract facts backfill (from `backend/`): `uv run python -m app.worker.backfill_contracts`; check against ground truth: `uv run python ../evals/check_extraction.py`
- Agent evals (from `backend/`): `uv run python ../evals/run_agent_evals.py --types contract_lookup --max-llm-calls 25 --label m6`
- Evals (from `backend/`): `uv run python ../evals/generate_corpus.py`, `build_questions.py`, `load_corpus.py`, `run_evals.py --sets easy hard --modes vector hybrid hybrid_rerank --label m5`

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
