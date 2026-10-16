# Groundwork journal (interview reference)

## Major decisions
| Date | Decision | Alternatives | Why |
|---|---|---|---|
| 2026-10-16 | Job queue = Postgres table with `FOR UPDATE SKIP LOCKED` | SQS, Redis/Celery | No extra infra, transactional with the document insert, portable across AWS/Oracle |
| 2026-10-16 | Hand-written tool-calling agent loop | LangChain, LangGraph | Shows understanding of the mechanics; fewer dependencies; full control of limits and citation validation |
| 2026-10-16 | Host-agnostic deploy (Docker Compose, S3-compatible storage, plain Postgres+pgvector) | AWS-native services (Lambda, Cognito, etc.) | AWS free tier ends; planned move to Oracle free tier must be config-only |
| 2026-10-16 | Strict AWS cost/secret guardrails (budget alarm, no NAT/multi-AZ, SSM, instance roles, gitleaks, user runs all AWS mutations) | Ad-hoc | Avoid leaked keys and surprise bills on a free-tier account |
| 2026-10-16 | No Co-Authored-By trailers in commits | Default attribution | Owner's preference: the repo history is the author's own work |
| 2026-10-16 | graphify knowledge graph for repo navigation | Raw grep each session | Cheaper context, persistent architecture map |

## Roadblocks
| Date | Symptom | Root cause | Fix | Lesson |
|---|---|---|---|---|
| | | | | |
