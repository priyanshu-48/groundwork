# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 21 files · ~5,878 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .example 1, .ini 1)

## Summary
- 119 nodes · 158 edges · 17 communities (9 shown, 8 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 3 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `d607b4f8`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- 8. Milestones (about 3 weeks, one Claude Code session each)
- Groundwork: instructions for Claude Code
- 6. Key designs (know these well, because they are the interview questions)
- Groundwork journal (interview reference)
- storage.py
- conftest.py
- get_settings
- main.py
- 0001-local-s3-rustfs.md
- groundwork

## God Nodes (most connected - your core abstractions)
1. `Groundwork: Build Spec` - 14 edges
2. `get_settings()` - 12 edges
3. `8. Milestones (about 3 weeks, one Claude Code session each)` - 12 edges
4. `make_engine()` - 9 edges
5. `Groundwork: instructions for Claude Code` - 9 edges
6. `6. Key designs (know these well, because they are the interview questions)` - 8 edges
7. `health()` - 7 edges
8. `lifespan()` - 6 edges
9. `Settings` - 5 edges
10. `create_app()` - 5 edges

## Surprising Connections (you probably didn't know these)
- `make_s3()` --uses--> `Settings`  [INFERRED]
  backend/app/services/storage.py → backend/app/config.py
- `health()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/api/health.py → backend/app/config.py
- `lifespan()` --calls--> `get_settings()`  [EXTRACTED]
  backend/app/main.py → backend/app/config.py
- `lifespan()` --calls--> `make_engine()`  [EXTRACTED]
  backend/app/main.py → backend/app/db.py
- `client()` --calls--> `create_app()`  [EXTRACTED]
  backend/tests/conftest.py → backend/app/main.py

## Import Cycles
- None detected.

## Communities (17 total, 8 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.15
Nodes (12): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+4 more)

### Community 1 - "8. Milestones (about 3 weeks, one Claude Code session each)"
Cohesion: 0.17
Nodes (12): 8. Milestones (about 3 weeks, one Claude Code session each), M0 — Skeleton (Day 1), M10 — Polish for recruiters (Days 20–21), M1 — Auth + tenancy (Day 2), M2 — Upload, S3, idempotency, job queue (Days 3–4), M3 — Ingestion worker (Days 5–6), M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8), M5 — Hybrid search + reranking (Days 9–10) (+4 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.20
Nodes (9): Commands, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal, Rules (+1 more)

### Community 3 - "6. Key designs (know these well, because they are the interview questions)"
Cohesion: 0.25
Nodes (8): 6.1 Idempotent upload, 6.2 Job queue with SKIP LOCKED, 6.3 Ingestion pipeline (worker), 6.4 Hybrid retrieval + reranking, 6.5 Agent loop (hand-written), 6.6 Streaming API, 6.7 Multi-tenancy, 6. Key designs (know these well, because they are the interview questions)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "storage.py"
Cohesion: 0.15
Nodes (4): _db_ok(), health(), Settings, s3_ok()

### Community 6 - "conftest.py"
Cohesion: 0.15
Nodes (4): client(), configured(), pg(), s3()

### Community 7 - "get_settings"
Cohesion: 0.20
Nodes (8): _run(), _run_online(), get_settings(), make_engine(), test_health_degraded_when_s3_missing(), test_health_ok(), test_migration_enabled_pgvector(), q()

### Community 8 - "main.py"
Cohesion: 0.39
Nodes (3): create_app(), lifespan(), make_s3()

## Knowledge Gaps
- **41 isolated node(s):** `groundwork`, `0001: RustFS instead of MinIO for local/test S3`, `Major decisions`, `Roadblocks`, `10. How to work with Claude Code on this` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 74 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `main.py`, `storage.py`, `conftest.py`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Why does `Groundwork: Build Spec` connect `Groundwork: Build Spec` to `8. Milestones (about 3 weeks, one Claude Code session each)`, `6. Key designs (know these well, because they are the interview questions)`?**
  _High betweenness centrality (0.058) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `8. Milestones (about 3 weeks, one Claude Code session each)` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.041) - this node is a cross-community bridge._
- **What connects `groundwork`, `0001: RustFS instead of MinIO for local/test S3`, `Major decisions` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `storage.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14619883040935672 - nodes in this community are weakly interconnected._
- **Should `conftest.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14705882352941177 - nodes in this community are weakly interconnected._