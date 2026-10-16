# Graph Report - groundwork  (2026-10-16)

## Corpus Check
- 68 files · ~15,100 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 8 file(s) not represented in the graph (top: (none) 4, .example 1, .ini 1)

## Summary
- 501 nodes · 1277 edges · 35 communities (19 shown, 16 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 79 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `88a40d90`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- sqlalchemy
- extraction.py
- tests/conftest.py
- api/auth.py
- 0001-local-s3-rustfs.md
- test_ingestion.py
- groundwork
- test_auth.py
- runner.py
- 0002-approximate-token-counts.md
- api/documents.py
- ingestion.py
- get_settings
- worker/deps.py
- build_deps
- storage.py
- main.py

## God Nodes (most connected - your core abstractions)
1. `Deps` - 36 edges
2. `get_settings()` - 27 edges
3. `process_one()` - 21 edges
4. `seed()` - 20 edges
5. `chunk_pages()` - 19 edges
6. `new_org()` - 18 edges
7. `words()` - 17 edges
8. `make_engine()` - 17 edges
9. `FakeEmbeddingProvider` - 16 edges
10. `test_crash_before_commit_leaves_nothing_and_rerun_has_no_duplicates()` - 16 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py
- `M3 — Ingestion worker (Days 5–6)` --references--> `EmbeddingProvider`  [INFERRED]
  SPEC.md → backend/app/services/embeddings.py
- `M3 — Ingestion worker (Days 5–6)` --references--> `FakeEmbeddingProvider`  [INFERRED]
  SPEC.md → backend/app/services/embeddings.py
- `make_s3()` --uses--> `Settings`  [INFERRED]
  backend/app/services/storage.py → backend/app/config.py

## Import Cycles
- None detected.

## Communities (35 total, 16 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "test_documents.py"
Cohesion: 0.47
Nodes (10): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected(), test_requires_auth() (+2 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.20
Nodes (9): Commands, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal, Rules (+1 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.12
Nodes (13): EmbeddingError, GeminiEmbeddingProvider, _normalize(), _cos(), _provider(), StubModels, test_fake_related_text_scores_higher_than_unrelated(), test_gemini_batches_of_50_and_normalizes() (+5 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.11
Nodes (12): Base, IdMixin, Document, Job, JobStatus, Org, User, create_with_job() (+4 more)

### Community 6 - "extraction.py"
Cohesion: 0.10
Nodes (17): _date(), InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason(), call_with_retry(), is_retryable() (+9 more)

### Community 7 - "tests/conftest.py"
Cohesion: 0.13
Nodes (6): client(), configured(), pg(), s3(), sql(), run()

### Community 8 - "api/auth.py"
Cohesion: 0.09
Nodes (25): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+17 more)

### Community 12 - "test_ingestion.py"
Cohesion: 0.12
Nodes (38): chunk_pages(), extract_pages(), put_pdf(), Deps, process_one(), run_worker(), invoice_text(), make_due() (+30 more)

### Community 17 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 19 - "runner.py"
Cohesion: 0.11
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "api/documents.py"
Cohesion: 0.11
Nodes (6): list_documents(), _read_pdf(), upload(), DocKind, DocStatus, DocumentOut

### Community 22 - "ingestion.py"
Cohesion: 0.09
Nodes (11): Chunk, Invoice, replace_for_document(), delete_for_document(), find_trusted(), TextChunk, ingest_document(), mark_failed() (+3 more)

### Community 23 - "get_settings"
Cohesion: 0.22
Nodes (9): _run(), _run_online(), get_settings(), make_engine(), go(), test_health_degraded_when_s3_missing(), test_health_ok(), test_migration_enabled_pgvector() (+1 more)

### Community 24 - "worker/deps.py"
Cohesion: 0.19
Nodes (6): EmbeddingProvider, FakeEmbeddingProvider, FakeInvoiceExtractor, deps(), test_fake_is_deterministic_768d_and_unit_norm(), M3 — Ingestion worker (Days 5–6)

### Community 26 - "build_deps"
Cohesion: 0.20
Nodes (5): Settings, GeminiInvoiceExtractor, make_client(), build_deps(), main()

### Community 27 - "storage.py"
Cohesion: 0.25
Nodes (3): _db_ok(), health(), s3_ok()

### Community 28 - "main.py"
Cohesion: 0.48
Nodes (3): create_app(), lifespan(), make_s3()

## Knowledge Gaps
- **41 isolated node(s):** `groundwork`, `0002: Approximate token counts for chunking`, `Major decisions`, `Roadblocks`, `JobStatus` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 183 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **16 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `worker/deps.py`?**
  _High betweenness centrality (0.107) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `tests/conftest.py`, `api/auth.py`, `test_auth.py`, `runner.py`, `api/documents.py`, `worker/deps.py`, `config.py`, `build_deps`, `storage.py`, `main.py`?**
  _High betweenness centrality (0.094) - this node is a cross-community bridge._
- **Are the 27 inferred relationships involving `Deps` (e.g. with `ingest_document()` and `mark_failed()`) actually correct?**
  _`Deps` has 27 INFERRED edges - model-reasoned connections that need verification._
- **What connects `groundwork`, `0002: Approximate token counts for chunking`, `Major decisions` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `test_embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1206896551724138 - nodes in this community are weakly interconnected._
- **Should `sqlalchemy` be split into smaller, more focused modules?**
  _Cohesion score 0.10638297872340426 - nodes in this community are weakly interconnected._