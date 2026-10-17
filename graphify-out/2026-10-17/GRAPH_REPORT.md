# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 120 files · ~67,912 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1111 nodes · 3157 edges · 75 communities (42 shown, 33 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 230 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f238874e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- sqlalchemy
- runner.py
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- new_org
- groundwork
- test_gemini_llm.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- make_engine
- build_ground_truth
- Deps
- generate_corpus.py
- test_rrf.py
- tools.py
- load_corpus.py
- extraction.py
- tests/conftest.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- run_agent_evals.py
- ingestion.py
- ingest_corpus
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- Message
- storage.py
- integration/conftest.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- small
- run_evals.py
- loop.py
- FakeEmbeddingProvider
- test_agent_evals.py
- test_metrics.py
- test_build_retrieval_questions.py
- build_questions.py
- pytest
- typing
- worker/deps.py
- PrecomputedEmbedder

## God Nodes (most connected - your core abstractions)
1. `Deps` - 105 edges
2. `new_org()` - 48 edges
3. `get_settings()` - 34 edges
4. `process_one()` - 28 edges
5. `seed()` - 28 edges
6. `search_documents()` - 28 edges
7. `Hit` - 26 edges
8. `build_deps()` - 25 edges
9. `DocKind` - 24 edges
10. `AgentContext` - 23 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
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

## Communities (75 total, 33 thin omitted)

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
Cohesion: 0.10
Nodes (18): EmbeddingError, GeminiEmbeddingProvider, Throttle, embed(), _cos(), _provider(), StubModels, test_fake_is_deterministic_768d_and_unit_norm() (+10 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.08
Nodes (24): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus (+16 more)

### Community 6 - "runner.py"
Cohesion: 0.15
Nodes (3): reap_stale(), run_reaper(), run_worker()

### Community 7 - "test_scoring.py"
Cohesion: 0.17
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.07
Nodes (36): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+28 more)

### Community 12 - "new_org"
Cohesion: 0.09
Nodes (47): chunk_pages(), TextChunk, extract_pages(), PermanentError, backfill(), BackfillResult, _next_batch(), process_one() (+39 more)

### Community 17 - "test_gemini_llm.py"
Cohesion: 0.14
Nodes (16): clean_schema(), GeminiLLM, LLMError, parse_response(), ToolCall, specs(), llm_with(), response() (+8 more)

### Community 19 - "test_queue.py"
Cohesion: 0.20
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.16
Nodes (13): keyword_search(), search_documents(), corpus(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+5 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.16
Nodes (18): retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over(), call() (+10 more)

### Community 23 - "make_engine"
Cohesion: 0.19
Nodes (9): _run(), _run_online(), make_engine(), run(), go(), test_health_degraded_when_s3_missing(), test_health_ok(), test_migration_enabled_pgvector() (+1 more)

### Community 24 - "build_ground_truth"
Cohesion: 0.26
Nodes (8): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth()

### Community 25 - "Deps"
Cohesion: 0.12
Nodes (44): call(), FakeLLM, say(), Usage, make_context(), execute(), Deps, add_invoice_row() (+36 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.15
Nodes (11): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+3 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.06
Nodes (33): AgentContext, _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs (+25 more)

### Community 29 - "load_corpus.py"
Cohesion: 0.14
Nodes (9): _auth(), main(), _main(), _retry(), _statuses(), _upload(), list_models(), main() (+1 more)

### Community 30 - "extraction.py"
Cohesion: 0.06
Nodes (28): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason() (+20 more)

### Community 31 - "tests/conftest.py"
Cohesion: 0.13
Nodes (8): client(), configured(), pg(), s3(), sql(), _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips()

### Community 33 - "Evaluation results"
Cohesion: 0.50
Nodes (3): Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "run_agent_evals.py"
Cohesion: 0.13
Nodes (13): test_cache_keys_change_with_the_model_chain_and_search_mode(), test_eval_queries_are_never_throttled(), append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache() (+5 more)

### Community 37 - "ingestion.py"
Cohesion: 0.07
Nodes (21): list_documents(), _read_pdf(), upload(), DocKind, DocStatus, Document, Invoice, create_with_job() (+13 more)

### Community 38 - "ingest_corpus"
Cohesion: 0.29
Nodes (6): ingest_corpus(), Recording, test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task(), test_questions_find_their_contract_and_mostly_their_page(), test_results_are_ranked_capped_and_filterable()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "Message"
Cohesion: 0.26
Nodes (8): LLM, LLMResponse, Message, _to_content(), ToolSpec, test_messages_become_gemini_contents(), test_raw_model_content_is_replayed_verbatim(), CountingLLM

### Community 44 - "storage.py"
Cohesion: 0.25
Nodes (3): _db_ok(), health(), s3_ok()

### Community 45 - "integration/conftest.py"
Cohesion: 0.29
Nodes (4): create_app(), lifespan(), make_s3(), deps()

### Community 52 - "run_evals.py"
Cohesion: 0.13
Nodes (13): test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), test_percentile_interpolates(), percentile(), append_docs_row() (+5 more)

### Community 53 - "loop.py"
Cohesion: 0.17
Nodes (8): ToolResult, AgentEvent, run_agent(), snippet(), _step_limit_answer(), validate_citations(), ask(), ConversationNotFound

### Community 54 - "FakeEmbeddingProvider"
Cohesion: 0.16
Nodes (5): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), UnrelatedQueryEmbedder, M3 — Ingestion worker (Days 5–6)

### Community 55 - "test_agent_evals.py"
Cohesion: 0.29
Nodes (8): LLMUnavailable, CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes()

### Community 57 - "test_metrics.py"
Cohesion: 0.46
Nodes (5): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), recall_at_k()

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.19
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 60 - "build_questions.py"
Cohesion: 0.33
Nodes (7): _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "pytest"
Cohesion: 0.22
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 62 - "typing"
Cohesion: 0.14
Nodes (5): call_with_retry(), _fall_over_seconds(), is_retryable(), ModelChain, test_daily_quota_429_is_not_retried_but_per_minute_429_is()

### Community 65 - "worker/deps.py"
Cohesion: 0.21
Nodes (8): get_settings(), model_chain_names(), Settings, make_client(), main(), _main(), build_deps(), main()

## Knowledge Gaps
- **53 isolated node(s):** `Tool`, `JobStatus`, `10. How to work with Claude Code on this`, `11. Metrics to capture (fill these in as you go)`, `12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure)` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 340 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **33 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `worker/deps.py`, `ingestion.py`, `runner.py`, `ingest_corpus`, `new_org`, `integration/conftest.py`, `run_evals.py`, `loop.py`, `FakeEmbeddingProvider`, `test_agent_evals.py`, `test_search_modes.py`, `extraction.py`?**
  _High betweenness centrality (0.103) - this node is a cross-community bridge._
- **Why does `search_documents()` connect `test_search_modes.py` to `Groundwork: Build Spec`, `ingestion.py`, `ingest_corpus`, `run_evals.py`, `FakeEmbeddingProvider`, `test_rrf.py`, `tools.py`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `worker/deps.py` to `run_agent_evals.py`, `ingestion.py`, `runner.py`, `api/auth.py`, `storage.py`, `integration/conftest.py`, `test_queue.py`, `run_evals.py`, `make_engine`, `tests/conftest.py`?**
  _High betweenness centrality (0.037) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 87 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `10. How to work with Claude Code on this` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `test_embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09747899159663866 - nodes in this community are weakly interconnected._