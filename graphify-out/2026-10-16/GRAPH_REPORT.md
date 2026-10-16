# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 46 files · ~9,753 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .example 1, .ini 1)

## Summary
- 312 nodes · 648 edges · 27 communities (12 shown, 15 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 26 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `2639b721`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- repositories/documents.py
- Groundwork journal (interview reference)
- queue.py
- api/auth.py
- get_settings
- security.py
- 0001-local-s3-rustfs.md
- groundwork
- test_auth.py
- test_queue.py
- api/documents.py

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 23 edges
2. `enqueue()` - 15 edges
3. `Groundwork: Build Spec` - 14 edges
4. `make_engine()` - 13 edges
5. `upload()` - 12 edges
6. `8. Milestones (about 3 weeks, one Claude Code session each)` - 12 edges
7. `claim()` - 11 edges
8. `maker()` - 11 edges
9. `current_user()` - 11 edges
10. `create_token()` - 11 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `create_with_job()` --uses--> `DocKind`  [INFERRED]
  backend/app/repositories/documents.py → backend/app/models/document.py
- `enqueue()` --uses--> `Job`  [INFERRED]
  backend/app/worker/queue.py → backend/app/models/job.py
- `me()` --uses--> `Principal`  [INFERRED]
  backend/app/api/auth.py → backend/app/services/security.py
- `login()` --indirect_call--> `verify_password()`  [INFERRED]
  backend/app/api/auth.py → backend/app/services/security.py

## Import Cycles
- None detected.

## Communities (27 total, 15 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "test_documents.py"
Cohesion: 0.47
Nodes (10): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected(), test_requires_auth() (+2 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.20
Nodes (9): Commands, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal, Rules (+1 more)

### Community 3 - "repositories/documents.py"
Cohesion: 0.29
Nodes (4): Document, create_with_job(), get_by_sha(), list_for_org()

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "queue.py"
Cohesion: 0.13
Nodes (9): Base, IdMixin, Job, JobStatus, Org, User, create_org_with_user(), get_user_by_email() (+1 more)

### Community 6 - "api/auth.py"
Cohesion: 0.22
Nodes (9): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+1 more)

### Community 7 - "get_settings"
Cohesion: 0.06
Nodes (22): _run(), _run_online(), _db_ok(), health(), get_settings(), Settings, make_engine(), create_app() (+14 more)

### Community 8 - "security.py"
Cohesion: 0.14
Nodes (16): current_user(), _unauthorized(), create_token(), decode_token(), hash_password(), Principal, TokenError, verify_password() (+8 more)

### Community 17 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 19 - "test_queue.py"
Cohesion: 0.14
Nodes (15): claim(), complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker(), _row() (+7 more)

### Community 21 - "api/documents.py"
Cohesion: 0.09
Nodes (8): get_session(), list_documents(), _read_pdf(), upload(), DocKind, DocStatus, DocumentOut, put_pdf()

## Knowledge Gaps
- **41 isolated node(s):** `JobStatus`, `groundwork`, `Major decisions`, `Roadblocks`, `10. How to work with Claude Code on this` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 132 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `api/auth.py`, `security.py`, `test_auth.py`, `test_queue.py`, `api/documents.py`?**
  _High betweenness centrality (0.190) - this node is a cross-community bridge._
- **Why does `current_user()` connect `security.py` to `api/documents.py`, `api/auth.py`, `get_settings`?**
  _High betweenness centrality (0.187) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `security.py`?**
  _High betweenness centrality (0.165) - this node is a cross-community bridge._
- **What connects `JobStatus`, `groundwork`, `Major decisions` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `queue.py` be split into smaller, more focused modules?**
  _Cohesion score 0.12941176470588237 - nodes in this community are weakly interconnected._
- **Should `get_settings` be split into smaller, more focused modules?**
  _Cohesion score 0.06284153005464481 - nodes in this community are weakly interconnected._