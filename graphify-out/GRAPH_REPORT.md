# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 35 files · ~7,191 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .example 1, .ini 1)

## Summary
- 208 nodes · 385 edges · 19 communities (10 shown, 9 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d607b4f8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- 8. Milestones (about 3 weeks, one Claude Code session each)
- Groundwork: instructions for Claude Code
- test_security.py
- Groundwork journal (interview reference)
- base.py
- conftest.py
- get_settings
- api/auth.py
- 0001-local-s3-rustfs.md
- groundwork
- test_auth.py

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 18 edges
2. `Groundwork: Build Spec` - 14 edges
3. `8. Milestones (about 3 weeks, one Claude Code session each)` - 12 edges
4. `create_token()` - 11 edges
5. `decode_token()` - 11 edges
6. `current_user()` - 10 edges
7. `TokenError` - 10 edges
8. `make_engine()` - 9 edges
9. `Groundwork: instructions for Claude Code` - 9 edges
10. `signup()` - 8 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `me()` --uses--> `Principal`  [INFERRED]
  backend/app/api/auth.py → backend/app/services/security.py
- `test_verify_garbage_hash_is_false()` --calls--> `verify_password()`  [EXTRACTED]
  backend/tests/unit/test_security.py → backend/app/services/security.py
- `_token()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/api/auth.py → backend/app/config.py
- `_token()` --calls--> `create_token()`  [EXTRACTED]
  backend/app/api/auth.py → backend/app/services/security.py

## Import Cycles
- None detected.

## Communities (19 total, 9 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.10
Nodes (20): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+12 more)

### Community 1 - "8. Milestones (about 3 weeks, one Claude Code session each)"
Cohesion: 0.18
Nodes (11): 8. Milestones (about 3 weeks, one Claude Code session each), M0 — Skeleton (Day 1), M10 — Polish for recruiters (Days 20–21), M2 — Upload, S3, idempotency, job queue (Days 3–4), M3 — Ingestion worker (Days 5–6), M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8), M5 — Hybrid search + reranking (Days 9–10), M6 — Agent loop + tools + citations (Days 11–12) (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.20
Nodes (9): Commands, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal, Rules (+1 more)

### Community 3 - "test_security.py"
Cohesion: 0.11
Nodes (14): current_user(), get_session(), _unauthorized(), create_token(), decode_token(), Principal, TokenError, test_alg_none_rejected() (+6 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "base.py"
Cohesion: 0.21
Nodes (6): Base, IdMixin, Org, User, create_org_with_user(), get_user_by_email()

### Community 6 - "conftest.py"
Cohesion: 0.18
Nodes (3): configured(), pg(), s3()

### Community 7 - "get_settings"
Cohesion: 0.08
Nodes (16): _run(), _run_online(), _db_ok(), health(), get_settings(), Settings, make_engine(), create_app() (+8 more)

### Community 8 - "api/auth.py"
Cohesion: 0.16
Nodes (12): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+4 more)

### Community 17 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

## Knowledge Gaps
- **40 isolated node(s):** `groundwork`, `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Hosting portability` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 95 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `current_user()` connect `test_security.py` to `api/auth.py`, `get_settings`?**
  _High betweenness centrality (0.252) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `8. Milestones (about 3 weeks, one Claude Code session each)` to `Groundwork: Build Spec`, `test_security.py`?**
  _High betweenness centrality (0.230) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `api/auth.py`, `test_auth.py`, `test_security.py`, `conftest.py`?**
  _High betweenness centrality (0.227) - this node is a cross-community bridge._
- **What connects `groundwork`, `Rules`, `Git` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `test_security.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11174242424242424 - nodes in this community are weakly interconnected._
- **Should `get_settings` be split into smaller, more focused modules?**
  _Cohesion score 0.08383838383838384 - nodes in this community are weakly interconnected._