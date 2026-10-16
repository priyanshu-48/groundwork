# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 4 files · ~4,638 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 4 file(s) not represented in the graph (top: (none) 2, .graphify-bak 1, .example 1)

## Summary
- 47 nodes · 44 edges · 5 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Groundwork: Build Spec
- 8. Milestones (about 3 weeks, one Claude Code session each)
- Groundwork: instructions for Claude Code
- 6. Key designs (know these well, because they are the interview questions)
- Groundwork journal (interview reference)

## God Nodes (most connected - your core abstractions)
1. `Groundwork: Build Spec` - 14 edges
2. `8. Milestones (about 3 weeks, one Claude Code session each)` - 12 edges
3. `Groundwork: instructions for Claude Code` - 9 edges
4. `6. Key designs (know these well, because they are the interview questions)` - 8 edges
5. `Groundwork journal (interview reference)` - 3 edges
6. `Rules` - 1 edges
7. `Git` - 1 edges
8. `Secrets and AWS cost safety (strict)` - 1 edges
9. `Hosting portability` - 1 edges
10. `Interview journal` - 1 edges

## Surprising Connections (you probably didn't know these)
- None detected - all connections are within the same source files.

## Communities (5 total, 0 thin omitted)

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

## Knowledge Gaps
- **39 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Hosting portability`, `Interview journal` (+34 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 42 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Groundwork: Build Spec` connect `Groundwork: Build Spec` to `8. Milestones (about 3 weeks, one Claude Code session each)`, `6. Key designs (know these well, because they are the interview questions)`?**
  _High betweenness centrality (0.388) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `8. Milestones (about 3 weeks, one Claude Code session each)` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.276) - this node is a cross-community bridge._
- **Why does `6. Key designs (know these well, because they are the interview questions)` connect `6. Key designs (know these well, because they are the interview questions)` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.189) - this node is a cross-community bridge._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _39 weakly-connected nodes found - possible documentation gaps or missing edges._