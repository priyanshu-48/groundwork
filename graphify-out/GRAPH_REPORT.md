# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 119 files · ~66,708 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1090 nodes · 3098 edges · 67 communities (42 shown, 25 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 212 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3307792d`
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
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- evaluate
- runner.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- get_settings
- Hit
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- run_evals.py
- extraction.py
- tests/conftest.py
- llm.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- typing
- upload
- test_gemini_llm.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- test_migrations.py
- storage.py
- chunks.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- run_agent_evals.py
- test_eval_harness.py
- search_documents
- loop.py
- Message
- embeddings.py
- test_build_retrieval_questions.py
- test_agent_evals.py
- build_questions.py
- test_build_questions.py
- retrieval.py
- PrecomputedEmbedder

## God Nodes (most connected - your core abstractions)
1. `Deps` - 111 edges
2. `new_org()` - 46 edges
3. `get_settings()` - 34 edges
4. `seed()` - 28 edges
5. `process_one()` - 28 edges
6. `search_documents()` - 28 edges
7. `Hit` - 26 edges
8. `build_deps()` - 24 edges
9. `Message` - 22 edges
10. `make_pdf()` - 21 edges

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

## Communities (67 total, 25 thin omitted)

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
Cohesion: 0.13
Nodes (15): EmbeddingError, GeminiEmbeddingProvider, is_retryable(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is(), test_fake_is_deterministic_768d_and_unit_norm() (+7 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.06
Nodes (24): _base(), upgrade(), Base, IdMixin, Chunk, DocStatus, Document, Invoice (+16 more)

### Community 6 - "worker/deps.py"
Cohesion: 0.19
Nodes (7): model_chain_names(), Settings, make_client(), make_s3(), main(), _main(), build_deps()

### Community 7 - "test_scoring.py"
Cohesion: 0.17
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.07
Nodes (35): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+27 more)

### Community 12 - "Deps"
Cohesion: 0.07
Nodes (67): chunk_pages(), TextChunk, ingest_document(), mark_failed(), store_invoice(), _store_invoice(), extract_pages(), PermanentError (+59 more)

### Community 17 - "evaluate"
Cohesion: 0.19
Nodes (10): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), evaluate() (+2 more)

### Community 19 - "runner.py"
Cohesion: 0.11
Nodes (17): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), main() (+9 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.15
Nodes (13): DocKind, corpus(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input() (+5 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "get_settings"
Cohesion: 0.19
Nodes (10): _run(), _run_online(), get_settings(), make_engine(), go(), deps(), test_health_degraded_when_s3_missing(), test_health_ok() (+2 more)

### Community 24 - "Hit"
Cohesion: 0.15
Nodes (10): Hit, FakeReranker, FlashRankReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.09
Nodes (42): call(), FakeLLM, say(), Usage, AgentEvent, ask(), ConversationNotFound, make_context() (+34 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.09
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.16
Nodes (15): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+7 more)

### Community 29 - "run_evals.py"
Cohesion: 0.12
Nodes (9): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+1 more)

### Community 30 - "extraction.py"
Cohesion: 0.08
Nodes (26): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason() (+18 more)

### Community 31 - "tests/conftest.py"
Cohesion: 0.18
Nodes (6): client(), configured(), pg(), s3(), sql(), run()

### Community 32 - "llm.py"
Cohesion: 0.11
Nodes (6): call_with_retry(), ModelChain, Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 33 - "Evaluation results"
Cohesion: 0.50
Nodes (3): Agent evals (M6), Evaluation results, Reproduce

### Community 37 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 38 - "test_gemini_llm.py"
Cohesion: 0.14
Nodes (15): clean_schema(), GeminiLLM, LLMError, parse_response(), ToolCall, llm_with(), response(), StubModels (+7 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "test_migrations.py"
Cohesion: 0.38
Nodes (3): _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips()

### Community 44 - "storage.py"
Cohesion: 0.25
Nodes (3): _db_ok(), health(), s3_ok()

### Community 45 - "chunks.py"
Cohesion: 0.23
Nodes (5): fetch_by_ids(), first_chunks(), keyword_search(), replace_for_document(), vector_search()

### Community 52 - "run_agent_evals.py"
Cohesion: 0.17
Nodes (13): LLM, test_cache_keys_change_with_the_model_chain_and_search_mode(), append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache() (+5 more)

### Community 53 - "test_eval_harness.py"
Cohesion: 0.18
Nodes (9): test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), append_docs_row(), _load() (+1 more)

### Community 54 - "search_documents"
Cohesion: 0.21
Nodes (7): search_documents(), ingest_corpus(), Recording, test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task(), test_questions_find_their_contract_and_mostly_their_page(), test_results_are_ranked_capped_and_filterable()

### Community 55 - "loop.py"
Cohesion: 0.24
Nodes (9): ToolResult, run_agent(), snippet(), _step_limit_answer(), validate_citations(), specs(), LLMUnavailable, test_model_outage_ends_the_run_cleanly() (+1 more)

### Community 56 - "Message"
Cohesion: 0.30
Nodes (7): LLMResponse, Message, _to_content(), ToolSpec, test_messages_become_gemini_contents(), test_raw_model_content_is_replayed_verbatim(), CountingLLM

### Community 57 - "embeddings.py"
Cohesion: 0.21
Nodes (4): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), M3 — Ingestion worker (Days 5–6)

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.18
Nodes (5): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions(), main()

### Community 59 - "test_agent_evals.py"
Cohesion: 0.35
Nodes (7): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes()

### Community 60 - "build_questions.py"
Cohesion: 0.36
Nodes (6): _aggregates(), build_questions(), _in_range(), _lookups(), _multi_hop(), _random_range()

### Community 61 - "test_build_questions.py"
Cohesion: 0.22
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

## Knowledge Gaps
- **53 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 331 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **25 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `sqlalchemy`, `worker/deps.py`, `runner.py`, `run_agent_evals.py`, `loop.py`, `search_documents`, `get_settings`, `test_eval_harness.py`, `test_agent_loop.py`, `test_search_modes.py`, `test_agent_evals.py`, `extraction.py`, `embeddings.py`?**
  _High betweenness centrality (0.092) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `typing`, `upload`, `worker/deps.py`, `sqlalchemy`, `api/auth.py`, `test_migrations.py`, `storage.py`, `runner.py`, `run_agent_evals.py`, `test_eval_harness.py`, `embeddings.py`, `tests/conftest.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `embeddings.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Are the 93 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 93 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `test_embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1339031339031339 - nodes in this community are weakly interconnected._