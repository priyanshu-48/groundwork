# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 94 files · ~54,292 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 755 nodes · 1957 edges · 45 communities (28 shown, 17 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 133 edges (avg confidence: 0.94)
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
- Deps
- groundwork
- run_evals.py
- runner.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- Throttle
- get_settings
- Hit
- worker/deps.py
- generate_corpus.py
- storage.py
- extraction.py
- explain_search.py
- test_extraction.py
- test_auth.py
- test_eval_harness.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- test_build_retrieval_questions.py
- precompute
- test_metrics.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 58 edges
2. `get_settings()` - 30 edges
3. `new_org()` - 30 edges
4. `search_documents()` - 26 edges
5. `process_one()` - 24 edges
6. `seed()` - 22 edges
7. `FakeEmbeddingProvider` - 21 edges
8. `DocKind` - 20 edges
9. `build_ground_truth()` - 20 edges
10. `chunk_pages()` - 19 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py
- `M3 — Ingestion worker (Days 5–6)` --references--> `EmbeddingProvider`  [INFERRED]
  SPEC.md → backend/app/services/embeddings.py

## Import Cycles
- None detected.

## Communities (45 total, 17 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.10
Nodes (20): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+12 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.07
Nodes (28): EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, is_retryable(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is() (+20 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "ingestion.py"
Cohesion: 0.07
Nodes (26): Base, IdMixin, Chunk, DocKind, DocStatus, Document, Invoice, Job (+18 more)

### Community 6 - "build_deps"
Cohesion: 0.22
Nodes (5): Settings, InvoiceExtractor, make_client(), build_deps(), main()

### Community 7 - "tests/conftest.py"
Cohesion: 0.15
Nodes (5): client(), configured(), pg(), s3(), sql()

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (28): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), list_documents() (+20 more)

### Community 12 - "Deps"
Cohesion: 0.10
Nodes (46): chunk_pages(), extract_pages(), PermanentError, put_pdf(), Deps, process_one(), run_worker(), ingest_corpus() (+38 more)

### Community 17 - "run_evals.py"
Cohesion: 0.17
Nodes (8): test_percentile_interpolates(), percentile(), eval_settings(), evaluate(), _git_sha(), _load(), main(), _main()

### Community 19 - "runner.py"
Cohesion: 0.11
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.08
Nodes (25): keyword_search(), prepare_keyword_query(), specific_terms(), rrf_fuse(), search_documents(), corpus(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind() (+17 more)

### Community 22 - "Throttle"
Cohesion: 0.18
Nodes (4): Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 23 - "get_settings"
Cohesion: 0.18
Nodes (11): _run(), _run_online(), get_settings(), make_engine(), run(), go(), deps(), test_health_degraded_when_s3_missing() (+3 more)

### Community 24 - "Hit"
Cohesion: 0.11
Nodes (9): Hit, FakeReranker, FlashRankReranker, Reranker, hit(), StubRanker, test_empty_candidates_skip_the_model(), test_fake_reranker_orders_by_word_overlap_and_caps_top_k() (+1 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.06
Nodes (32): small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs() (+24 more)

### Community 27 - "storage.py"
Cohesion: 0.22
Nodes (6): _db_ok(), health(), create_app(), lifespan(), make_s3(), s3_ok()

### Community 28 - "extraction.py"
Cohesion: 0.26
Nodes (5): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, _money(), call_with_retry()

### Community 29 - "explain_search.py"
Cohesion: 0.13
Nodes (9): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+1 more)

### Community 30 - "test_extraction.py"
Cohesion: 0.17
Nodes (12): InvoiceFields, _LLMInvoice, review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines() (+4 more)

### Community 31 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 32 - "test_eval_harness.py"
Cohesion: 0.24
Nodes (7): test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), build_retrieval_questions(), append_docs_row()

### Community 36 - "test_build_retrieval_questions.py"
Cohesion: 0.20
Nodes (3): gt(), qs(), test_counts_ids_and_determinism()

### Community 37 - "precompute"
Cohesion: 0.25
Nodes (3): test_precomputed_embedder_returns_the_stored_vectors(), precompute(), PrecomputedEmbedder

### Community 38 - "test_metrics.py"
Cohesion: 0.46
Nodes (5): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), recall_at_k()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

## Knowledge Gaps
- **49 isolated node(s):** `JobStatus`, `groundwork`, `Rules`, `Git`, `Secrets and AWS cost safety (strict)` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 257 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **17 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `test_eval_harness.py`, `build_deps`, `tests/conftest.py`, `api/auth.py`, `run_evals.py`, `runner.py`, `worker/deps.py`, `storage.py`, `test_auth.py`?**
  _High betweenness centrality (0.061) - this node is a cross-community bridge._
- **Why does `Deps` connect `Deps` to `test_eval_harness.py`, `test_embeddings.py`, `ingestion.py`, `build_deps`, `precompute`, `runner.py`, `test_search_modes.py`, `get_settings`, `worker/deps.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `test_embeddings.py` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Are the 46 inferred relationships involving `Deps` (e.g. with `ingest_document()` and `mark_failed()`) actually correct?**
  _`Deps` has 46 INFERRED edges - model-reasoned connections that need verification._
- **Are the 6 inferred relationships involving `search_documents()` (e.g. with `DocKind` and `Hit`) actually correct?**
  _`search_documents()` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `JobStatus`, `groundwork`, `Rules` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._