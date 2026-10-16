# Groundwork journal (interview reference)

## Major decisions
| Date | Decision | Alternatives | Why |
|---|---|---|---|
| 2026-10-16 | Job queue = Postgres table with `FOR UPDATE SKIP LOCKED` | SQS, Redis/Celery | No extra infra, transactional with the document insert, portable across AWS/Oracle |
| 2026-10-16 | Hand-written tool-calling agent loop | LangChain, LangGraph | Shows understanding of the mechanics; fewer dependencies; full control of limits and citation validation |
| 2026-10-16 | Host-agnostic deploy (Docker Compose, S3-compatible storage, plain Postgres+pgvector) | AWS-native services (Lambda, Cognito, etc.) | AWS free tier ends; planned move to Oracle free tier must be config-only |
| 2026-10-16 | Strict AWS cost/secret guardrails (budget alarm, no NAT/multi-AZ, SSM, instance roles, gitleaks, user runs all AWS mutations) | Ad-hoc | Avoid leaked keys and surprise bills on a free-tier account |
| 2026-10-16 | No Co-Authored-By trailers in commits | Default attribution | Owner's preference: the repo history is the author's own work |
| 2026-10-16 | RustFS replaces MinIO for local/test S3 | SeaweedFS, LocalStack, pinned old MinIO | MinIO's public images were removed; S3 API is the contract, so the app is unaffected (ADR 0001) |
| 2026-10-16 | M1 auth: argon2 hashing off the event loop, HS256 JWT (sub, org_id, exp) with algorithm whitelist, signup creates org+user, identical 401 for unknown email vs wrong password (dummy-hash verify), app refuses to boot without a 32+ char JWT_SECRET | bcrypt, refresh tokens, invites | argon2 is the current OWASP pick; to_thread keeps the loop responsive; whitelist blocks alg=none; no enumeration; fail-closed secret. org_id only ever comes from the verified token |
| 2026-10-16 | graphify knowledge graph for repo navigation | Raw grep each session | Cheaper context, persistent architecture map |

## Roadblocks
| Date | Symptom | Root cause | Fix | Lesson |
|---|---|---|---|---|
| 2026-10-16 | `docker compose up` api crashed: `No module named 'app'` in alembic env.py | Alembic CLI doesn't add cwd to sys.path; pytest masked it because rootdir was on the path | `prepend_sys_path = .` in alembic.ini | Test the container path, not just pytest |
| 2026-10-16 | Compose failed binding 5432 | Windows/another service already holds the port | Host port 5433 (container stays 5432) | Keep host ports configurable |
| 2026-10-16 | Testcontainers `ImageNotFound` for minio/minio | Upstream removed the image | Switched to RustFS | Pin and verify images early |
