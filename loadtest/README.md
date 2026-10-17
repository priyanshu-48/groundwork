# Load tests

Needs Docker. k6 runs from its image (`grafana/k6`), nothing to install. Run from the repo root;
`MSYS_NO_PATHCONV=1` is for Git Bash on Windows (use `$(pwd)` instead of `$(pwd -W)` elsewhere).

The default limits (20 chats/min, 60 searches/min per org, 5 sign-ups/min per IP) would throttle a
load test, so raise them for the stack under test only:

```bash
export SEARCH_RATE_LIMIT_PER_MIN=100000 SIGNUP_RATE_LIMIT_PER_MIN=100000 CHAT_RATE_LIMIT_PER_MIN=100000
docker compose up -d --build
```

**Search** (real embeddings: about 40 Gemini embedding requests; eval corpus loaded; `.env` holds EVAL_PASSWORD):

```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W)/loadtest:/lt" -e EVAL_PASSWORD=... -e RUN_ID=r1 grafana/k6 run --quiet /lt/k6_search.js
```

Change `RUN_ID` per run, or the cold phase hits the cache from the previous run.

**Chat overhead** (needs `AI_PROVIDER=fake` so no Gemini quota is used):

```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W)/loadtest:/lt" -e MODE=load -e VUS=10 grafana/k6 run --quiet /lt/k6_chat.js
```

**Limit check** (restart the API with the default `CHAT_RATE_LIMIT_PER_MIN=20`, fake provider):

```bash
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W)/loadtest:/lt" -e MODE=limit -e LIMIT=20 grafana/k6 run --quiet /lt/k6_chat.js
```

**Ingestion throughput** (fake provider for the worker too):

```bash
cd backend && uv run python ../loadtest/ingest_throughput.py --n 60 --pages 3
```
