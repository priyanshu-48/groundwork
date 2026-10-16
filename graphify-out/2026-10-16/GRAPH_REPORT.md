# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 35 files · ~7,191 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .example 1, .ini 1)

## Summary
- 210 nodes · 385 edges · 22 communities (11 shown, 11 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 18 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d49beaae`
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
- storage.py

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
- `current_user()` --uses--> `Principal`  [INFERRED]
  backend/app/api/deps.py → backend/app/services/security.py
- `current_user()` --uses--> `TokenError`  [INFERRED]
  backend/app/api/deps.py → backend/app/services/security.py
- `test_verify_garbage_hash_is_false()` --calls--> `verify_password()`  [EXTRACTED]
  backend/tests/unit/test_security.py → backend/app/services/security.py
- `_token()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/api/auth.py → backend/app/config.py

## Import Cycles
- None detected.

## Communities (22 total, 11 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.10
Nodes (20): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+12 more)

### Community 1 - "8. Milestones (about 3 weeks, one Claude Code session each)"
Cohesion: 0.12
Nodes (14): current_user(), _unauthorized(), 8. Milestones (about 3 weeks, one Claude Code session each), M0 — Skeleton (Day 1), M10 — Polish for recruiters (Days 20–21), M1 — Auth + tenancy (Day 2), M2 — Upload, S3, idempotency, job queue (Days 3–4), M3 — Ingestion worker (Days 5–6) (+6 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.20
Nodes (9): Commands, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal, Rules (+1 more)

### Community 3 - "test_security.py"
Cohesion: 0.22
Nodes (9): create_token(), decode_token(), TokenError, test_alg_none_rejected(), test_expired_token_rejected(), test_missing_org_claim_rejected(), test_token_round_trip(), test_verify_garbage_hash_is_false() (+1 more)

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
Cohesion: 0.09
Nodes (14): _run(), _run_online(), get_session(), get_settings(), Settings, make_engine(), create_app(), lifespan() (+6 more)

### Community 8 - "api/auth.py"
Cohesion: 0.15
Nodes (13): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+5 more)

### Community 17 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 19 - "storage.py"
Cohesion: 0.22
Nodes (3): _db_ok(), health(), s3_ok()

## Knowledge Gaps
- **40 isolated node(s):** `groundwork`, `Major decisions`, `Roadblocks`, `10. How to work with Claude Code on this`, `11. Metrics to capture (fill these in as you go)` (+35 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 97 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **11 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `current_user()` connect `8. Milestones (about 3 weeks, one Claude Code session each)` to `api/auth.py`, `test_security.py`, `get_settings`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `8. Milestones (about 3 weeks, one Claude Code session each)` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.226) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `8. Milestones (about 3 weeks, one Claude Code session each)`, `conftest.py`, `api/auth.py`, `test_auth.py`, `storage.py`?**
  _High betweenness centrality (0.222) - this node is a cross-community bridge._
- **What connects `groundwork`, `Major decisions`, `Roadblocks` to the rest of the system?**
  _40 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `8. Milestones (about 3 weeks, one Claude Code session each)` be split into smaller, more focused modules?**
  _Cohesion score 0.11764705882352941 - nodes in this community are weakly interconnected._
- **Should `get_settings` be split into smaller, more focused modules?**
  _Cohesion score 0.09388335704125178 - nodes in this community are weakly interconnected._