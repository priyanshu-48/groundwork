# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 85 files · ~48,262 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .example 1, .ini 1)

## Summary
- 654 nodes · 1683 edges · 35 communities (20 shown, 15 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.93)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f507ab7f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- ingestion.py
- build_deps
- tests/conftest.py
- api/auth.py
- 0001-local-s3-rustfs.md
- test_ingestion.py
- groundwork
- run_evals.py
- runner.py
- 0002-approximate-token-counts.md
- Throttle
- get_settings
- FakeEmbeddingProvider
- config.py
- generate_corpus.py
- storage.py
- worker/deps.py
- build_questions.py
- test_auth.py
- Evaluation results
- 0004-synthetic-corpus-design.md

## God Nodes (most connected - your core abstractions)
1. `get_settings()` - 30 edges
2. `Deps` - 28 edges
3. `process_one()` - 26 edges
4. `new_org()` - 26 edges
5. `seed()` - 25 edges
6. `build_ground_truth()` - 20 edges
7. `chunk_pages()` - 19 edges
8. `words()` - 17 edges
9. `make_engine()` - 17 edges
10. `build_deps()` - 17 edges

## Surprising Connections (you probably didn't know these)
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_retrieval.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py

## Import Cycles
- None detected.

## Communities (35 total, 15 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.17
Nodes (13): is_retryable(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is(), test_fake_is_deterministic_768d_and_unit_norm(), test_fake_related_text_scores_higher_than_unrelated(), test_gemini_batches_of_50_and_normalizes() (+5 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "ingestion.py"
Cohesion: 0.06
Nodes (28): Base, IdMixin, Chunk, DocKind, DocStatus, Document, Invoice, Job (+20 more)

### Community 6 - "build_deps"
Cohesion: 0.29
Nodes (4): Settings, make_client(), build_deps(), main()

### Community 7 - "tests/conftest.py"
Cohesion: 0.09
Nodes (12): client(), configured(), pg(), s3(), sql(), run(), _auth(), main() (+4 more)

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (28): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), list_documents() (+20 more)

### Community 12 - "test_ingestion.py"
Cohesion: 0.08
Nodes (48): chunk_pages(), TextChunk, extract_pages(), put_pdf(), Deps, process_one(), run_worker(), invoice_text() (+40 more)

### Community 17 - "run_evals.py"
Cohesion: 0.09
Nodes (14): test_eval_queries_are_never_throttled(), test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k() (+6 more)

### Community 19 - "runner.py"
Cohesion: 0.11
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 22 - "Throttle"
Cohesion: 0.18
Nodes (4): Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 23 - "get_settings"
Cohesion: 0.23
Nodes (8): _run(), _run_online(), get_settings(), make_engine(), go(), deps(), test_migration_enabled_pgvector(), q()

### Community 24 - "FakeEmbeddingProvider"
Cohesion: 0.15
Nodes (6): EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), M3 — Ingestion worker (Days 5–6)

### Community 26 - "generate_corpus.py"
Cohesion: 0.09
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "storage.py"
Cohesion: 0.21
Nodes (6): _db_ok(), health(), create_app(), lifespan(), make_s3(), s3_ok()

### Community 28 - "worker/deps.py"
Cohesion: 0.26
Nodes (5): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, _money()

### Community 30 - "build_questions.py"
Cohesion: 0.08
Nodes (24): InvoiceFields, _LLMInvoice, review_reason(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic() (+16 more)

### Community 31 - "test_auth.py"
Cohesion: 0.21
Nodes (13): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+5 more)

## Knowledge Gaps
- **41 isolated node(s):** `Reproduce`, `JobStatus`, `10. How to work with Claude Code on this`, `11. Metrics to capture (fill these in as you go)`, `12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure)` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 224 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **15 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `build_deps`, `tests/conftest.py`, `api/auth.py`, `test_ingestion.py`, `run_evals.py`, `runner.py`, `config.py`, `storage.py`, `worker/deps.py`, `test_auth.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `FakeEmbeddingProvider`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `FakeEmbeddingProvider` connect `FakeEmbeddingProvider` to `test_embeddings.py`, `build_deps`, `test_ingestion.py`, `get_settings`, `config.py`, `worker/deps.py`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Are the 17 inferred relationships involving `Deps` (e.g. with `Settings` and `EmbeddingProvider`) actually correct?**
  _`Deps` has 17 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Reproduce`, `JobStatus`, `10. How to work with Claude Code on this` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `ingestion.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05669050051072523 - nodes in this community are weakly interconnected._