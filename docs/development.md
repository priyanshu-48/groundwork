# Development commands

Run from the repository root unless a command says otherwise.

## Backend (`backend/`)
- Tests: `cd backend && uv run pytest` (integration tests start Postgres and an S3 server with Testcontainers, so Docker must be running)
- Before committing: `uv run ruff check . && uv run mypy app && uv run pytest`
- Coverage: `uv run pytest --cov=app`
- Migrations: `uv run alembic upgrade head`
- Worker: `uv run python -m app.worker.runner`
- Logs are JSON; metrics at `GET /admin/metrics` ([observability](observability.md))

## Frontend (`frontend/`)
- `npm run dev`, `npm test`, `npm run typecheck`, `npm run lint`, `npm run build`
- End-to-end test (needs the demo-mode backend on :8000): `npm run e2e`

## Run the whole stack locally
- Without an API key (offline demo model): `AI_PROVIDER=fake docker compose up -d --build` (UI at http://localhost:8080, or `npm run dev` on :5173)
- With a Gemini key (free tier): `GEMINI_API_KEY=... docker compose up -d --build`

## Data backfills (from `backend/`)
- Invoice extraction: `uv run python -m app.worker.backfill_invoices`
- Contract facts: `uv run python -m app.worker.backfill_contracts`; check against ground truth: `uv run python ../evals/check_extraction.py`

## Evaluations (from `backend/`; free-tier Gemini key and synthetic data only)
- Corpus and questions: `uv run python ../evals/generate_corpus.py`, then `../evals/build_questions.py`, then `../evals/load_corpus.py`
- Retrieval: `uv run python ../evals/run_evals.py --sets easy hard --modes vector hybrid hybrid_rerank --label m5`
- Agent: `uv run python ../evals/run_agent_evals.py --types contract_lookup --max-llm-calls 25 --label m6`
- Details and results: [evals.md](evals.md)

## Load tests
See [../loadtest/README.md](../loadtest/README.md) (k6 via Docker).

## Deploy
See [deploy.md](deploy.md) (AWS, run in CloudShell). A local rehearsal of the production stack and the public demo setup are in the same file. Check a live demo with `python deploy/common/smoke.py <url> --demo`.
