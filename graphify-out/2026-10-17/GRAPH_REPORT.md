# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 95 files · ~54,406 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 779 nodes · 1966 edges · 54 communities (30 shown, 24 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 97 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `787aa0c7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- sqlalchemy
- worker/deps.py
- search_documents
- api/auth.py
- 0001-local-s3-rustfs.md
- test_ingestion.py
- groundwork
- run_evals.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- Throttle
- get_settings
- Hit
- embeddings.py
- generate_corpus.py
- test_rrf.py
- .extract
- load_corpus.py
- test_extraction.py
- test_auth.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- test_build_retrieval_questions.py
- build_questions.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- keyword_search
- build_ground_truth
- chunks.py
- FakeEmbeddingProvider
- test_build_questions.py
- GeminiEmbeddingProvider
- small

## God Nodes (most connected - your core abstractions)
1. `Deps` - 35 edges
2. `get_settings()` - 30 edges
3. `new_org()` - 30 edges
4. `search_documents()` - 26 edges
5. `process_one()` - 24 edges
6. `seed()` - 22 edges
7. `Hit` - 20 edges
8. `build_ground_truth()` - 20 edges
9. `chunk_pages()` - 19 edges
10. `FakeEmbeddingProvider` - 18 edges

## Surprising Connections (you probably didn't know these)
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py
- `M3 — Ingestion worker (Days 5–6)` --references--> `EmbeddingProvider`  [INFERRED]
  SPEC.md → backend/app/services/embeddings.py

## Import Cycles
- None detected.

## Communities (54 total, 24 thin omitted)

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
Cohesion: 0.22
Nodes (11): EmbeddingError, _cos(), _provider(), StubModels, test_fake_related_text_scores_higher_than_unrelated(), test_gemini_batches_of_50_and_normalizes(), test_gemini_does_not_retry_client_errors(), test_gemini_gives_up_after_max_tries() (+3 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.08
Nodes (19): Base, IdMixin, Document, Invoice, Job, JobStatus, Org, User (+11 more)

### Community 6 - "worker/deps.py"
Cohesion: 0.16
Nodes (8): Settings, FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, make_client(), make_s3(), build_deps(), deps()

### Community 7 - "search_documents"
Cohesion: 0.17
Nodes (7): search_documents(), ingest_corpus(), Recording, test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task(), test_questions_find_their_contract_and_mostly_their_page(), test_results_are_ranked_capped_and_filterable()

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (28): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), list_documents() (+20 more)

### Community 12 - "test_ingestion.py"
Cohesion: 0.09
Nodes (47): DocKind, DocStatus, DocumentOut, chunk_pages(), ingest_document(), mark_failed(), extract_pages(), PermanentError (+39 more)

### Community 17 - "run_evals.py"
Cohesion: 0.08
Nodes (22): test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses() (+14 more)

### Community 19 - "test_queue.py"
Cohesion: 0.13
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.21
Nodes (11): corpus(), test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input(), test_keyword_uses_or_semantics_so_one_unmatched_word_does_not_zero_the_result(), test_rerank_mode_follows_the_reranker_and_limits_candidates() (+3 more)

### Community 22 - "Throttle"
Cohesion: 0.21
Nodes (4): Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 23 - "get_settings"
Cohesion: 0.07
Nodes (20): _run(), _run_online(), _db_ok(), health(), get_settings(), make_engine(), create_app(), lifespan() (+12 more)

### Community 24 - "Hit"
Cohesion: 0.12
Nodes (11): Hit, FakeReranker, FlashRankReranker, RecordingReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker (+3 more)

### Community 25 - "embeddings.py"
Cohesion: 0.19
Nodes (3): call_with_retry(), is_retryable(), test_daily_quota_429_is_not_retried_but_per_minute_429_is()

### Community 26 - "generate_corpus.py"
Cohesion: 0.15
Nodes (11): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+3 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 29 - "load_corpus.py"
Cohesion: 0.18
Nodes (6): _auth(), main(), _main(), _retry(), _statuses(), _upload()

### Community 30 - "test_extraction.py"
Cohesion: 0.17
Nodes (12): InvoiceFields, _LLMInvoice, review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines() (+4 more)

### Community 31 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 36 - "test_build_retrieval_questions.py"
Cohesion: 0.21
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 38 - "build_questions.py"
Cohesion: 0.31
Nodes (7): _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "keyword_search"
Cohesion: 0.21
Nodes (4): Chunk, keyword_search(), replace_for_document(), vector_search()

### Community 44 - "build_ground_truth"
Cohesion: 0.26
Nodes (8): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth()

### Community 46 - "FakeEmbeddingProvider"
Cohesion: 0.20
Nodes (5): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), test_fake_is_deterministic_768d_and_unit_norm(), M3 — Ingestion worker (Days 5–6)

### Community 47 - "test_build_questions.py"
Cohesion: 0.20
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

## Knowledge Gaps
- **49 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+44 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 271 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `worker/deps.py`, `api/auth.py`, `test_ingestion.py`, `run_evals.py`, `test_queue.py`, `test_auth.py`?**
  _High betweenness centrality (0.059) - this node is a cross-community bridge._
- **Why does `search_documents()` connect `search_documents` to `Groundwork: Build Spec`, `keyword_search`, `chunks.py`, `run_evals.py`, `test_search_modes.py`, `Hit`, `test_rrf.py`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `FakeEmbeddingProvider`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 22 inferred relationships involving `Deps` (e.g. with `ingest_document()` and `mark_failed()`) actually correct?**
  _`Deps` has 22 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `search_documents()` (e.g. with `Hit` and `Reranker`) actually correct?**
  _`search_documents()` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _49 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._