# 0012: In-memory rate limits and a static admin token
- **Context:** each chat spends free-tier model quota, and nothing stopped one tenant (or a bug) draining it. We also needed an operator-only metrics route; no roles exist yet.
- **Decision:** sliding-window limiter plus a per-org concurrency cap, held in process memory; IP-keyed limits on login/signup. `/admin/metrics` is guarded by a static `ADMIN_TOKEN` compared in constant time; unset means the route 404s.
- **Alternatives:** Redis or Postgres counters (shared across processes, but new infra or a write per request); roles/JWT claims for admin (nothing to attach them to yet).
- **Trade-offs:** with N API processes the effective limit is N times higher, and a restart resets counters. One process today; upgrade path is a Postgres or Redis counter behind the same `check()` interface. The token lives in SSM in production and is rotated by redeploying.
- **Found by test:** pruning idle keys inside `check()` once dropped the current key's deque and lost its hit.
