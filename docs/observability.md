# Observability (M8)

## Logs
One JSON object per line on stderr (API and worker): `ts, level, logger, msg`, plus `request_id`,
`org_id`, `job_id`, `document_id` when known. Each request writes one `groundwork.access` line with
`method, path, route, status, duration_ms`. Clients may send `X-Request-ID` (up to 64 chars of
`[A-Za-z0-9_-]`); otherwise one is generated. It is returned in the `X-Request-ID` response header, so
a user can quote it. Never logged: bodies, `Authorization`, emails, passwords, document text (a test
checks this). Level via `LOG_LEVEL`. Uvicorn's own access log is off.

## GET /admin/metrics
Header `X-Admin-Token: <ADMIN_TOKEN>`. Unset `ADMIN_TOKEN` = the route returns 404. Sections:
`http` (last 10k requests of this process, per route template: count, 5xx rate, p50/p95/p99; resets on
restart), `agent` (last 24 h from `agent_runs`: runs, status, latency, tokens, avg tool steps, runs and
tokens per model, so fallbacks are visible), `queue` (jobs by status, queue depth, oldest due job age,
stale running jobs, documents by status). Counts only, no tenant content.

## Cost
`estimated_cost_usd` = tokens x `MODEL_PRICES` (JSON, USD per 1M input/output tokens per model). A model
without a configured price gives `null` (and so does the total), never a guess. Only agent calls are
token-tracked; embedding and extraction calls are not. The free tier bills $0 whatever this says.

## Limits (per API process)
Chat: `CHAT_RATE_LIMIT_PER_MIN` (20) and `CHAT_MAX_CONCURRENT` (3) per org. Search:
`SEARCH_RATE_LIMIT_PER_MIN` (60) per org. `/auth/login` 10/min and `/auth/signup` 5/min per client IP
(`--proxy-headers` makes that the real client behind nginx). Over a limit: `429`, `Retry-After`, a
plain-language `detail`. A concurrency slot leaked by a request that died before streaming is reclaimed
after 5 minutes.
