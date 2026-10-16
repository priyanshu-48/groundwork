# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 84 files · ~47,695 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .example 1, .ini 1)

## Summary
- 644 nodes · 1695 edges · 34 communities (21 shown, 13 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbeda182`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_retrieval.py
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- api/documents.py
- ingestion.py
- tests/conftest.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- run_evals.py
- runner.py
- 0002-approximate-token-counts.md
- upload
- Throttle
- get_settings
- embeddings.py
- worker/deps.py
- generate_corpus.py
- storage.py
- extraction.py
- build_questions.py
- test_auth.py
- Evaluation results
- 0004-synthetic-corpus-design.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 45 edges
2. `get_settings()` - 30 edges
3. `process_one()` - 26 edges
4. `new_org()` - 26 edges
5. `seed()` - 25 edges
6. `build_ground_truth()` - 20 edges
7. `chunk_pages()` - 19 edges
8. `FakeEmbeddingProvider` - 19 edges
9. `make_engine()` - 17 edges
10. `DocKind` - 17 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_retrieval.py

## Import Cycles
- None detected.

## Communities (34 total, 13 thin omitted)

### Community 0 - "test_retrieval.py"
Cohesion: 0.05
Nodes (39): search_documents(), ingest(), Recording, small(), test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task(), test_questions_find_their_contract_and_mostly_their_page(), test_results_are_ranked_capped_and_filterable() (+31 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.16
Nodes (14): EmbeddingError, is_retryable(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is(), test_fake_is_deterministic_768d_and_unit_norm(), test_fake_related_text_scores_higher_than_unrelated() (+6 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "api/documents.py"
Cohesion: 0.07
Nodes (20): Base, IdMixin, Chunk, DocKind, DocStatus, Document, Job, JobStatus (+12 more)

### Community 6 - "ingestion.py"
Cohesion: 0.09
Nodes (21): Invoice, delete_for_document(), find_trusted(), InvoiceFields, _LLMInvoice, review_reason(), ingest_document(), mark_failed() (+13 more)

### Community 7 - "tests/conftest.py"
Cohesion: 0.15
Nodes (6): client(), configured(), pg(), s3(), sql(), run()

### Community 8 - "api/auth.py"
Cohesion: 0.08
Nodes (25): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+17 more)

### Community 12 - "Deps"
Cohesion: 0.12
Nodes (40): chunk_pages(), TextChunk, Deps, process_one(), run_worker(), invoice_text(), make_due(), make_pdf() (+32 more)

### Community 17 - "run_evals.py"
Cohesion: 0.12
Nodes (14): test_eval_queries_are_never_throttled(), test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k() (+6 more)

### Community 19 - "runner.py"
Cohesion: 0.12
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 22 - "Throttle"
Cohesion: 0.12
Nodes (6): GeminiEmbeddingProvider, call_with_retry(), Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 23 - "get_settings"
Cohesion: 0.19
Nodes (9): _run(), _run_online(), get_settings(), make_engine(), go(), test_health_degraded_when_s3_missing(), test_health_ok(), test_migration_enabled_pgvector() (+1 more)

### Community 24 - "embeddings.py"
Cohesion: 0.16
Nodes (5): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), deps(), M3 — Ingestion worker (Days 5–6)

### Community 26 - "generate_corpus.py"
Cohesion: 0.10
Nodes (19): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth() (+11 more)

### Community 27 - "storage.py"
Cohesion: 0.17
Nodes (6): _db_ok(), health(), create_app(), lifespan(), make_s3(), s3_ok()

### Community 28 - "extraction.py"
Cohesion: 0.20
Nodes (7): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, _money(), build_deps(), main()

### Community 30 - "build_questions.py"
Cohesion: 0.08
Nodes (18): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), _aggregates(), build_questions(), _in_range() (+10 more)

### Community 31 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

## Knowledge Gaps
- **41 isolated node(s):** `JobStatus`, `groundwork`, `Rules`, `Git`, `Secrets and AWS cost safety (strict)` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 216 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **13 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `api/documents.py`, `tests/conftest.py`, `api/auth.py`, `Deps`, `run_evals.py`, `runner.py`, `upload`, `embeddings.py`, `worker/deps.py`, `storage.py`, `extraction.py`, `test_auth.py`?**
  _High betweenness centrality (0.075) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `test_retrieval.py` to `embeddings.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `FakeEmbeddingProvider` connect `embeddings.py` to `test_retrieval.py`, `test_embeddings.py`, `Deps`, `run_evals.py`, `worker/deps.py`, `extraction.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Deps` (e.g. with `ingest_document()` and `mark_failed()`) actually correct?**
  _`Deps` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `JobStatus`, `groundwork`, `Rules` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_retrieval.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05272108843537415 - nodes in this community are weakly interconnected._
- **Should `api/documents.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07374254049445865 - nodes in this community are weakly interconnected._