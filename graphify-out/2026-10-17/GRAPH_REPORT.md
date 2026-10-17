# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 121 files · ~69,475 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1102 nodes · 3169 edges · 65 communities (37 shown, 28 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 245 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `0268917c`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- Hit
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- ingestion.py
- test_auth.py
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- Reranker
- runner.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- get_settings
- tools.py
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- invoices_tool
- explain_search.py
- InvoiceFields
- Evaluation results
- 0004-synthetic-corpus-design.md
- ModelChain
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- worker/deps.py
- tests/conftest.py
- evaluate
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- test_migrations.py
- test_agent_evals.py
- test_documents.py
- test_eval_harness.py
- GeminiEmbeddingProvider
- eval_settings
- PrecomputedEmbedder
- test_build_retrieval_questions.py
- build_questions.py
- test_build_questions.py
- chunks.py

## God Nodes (most connected - your core abstractions)
1. `Deps` - 114 edges
2. `new_org()` - 48 edges
3. `get_settings()` - 34 edges
4. `process_one()` - 28 edges
5. `seed()` - 28 edges
6. `search_documents()` - 28 edges
7. `Hit` - 26 edges
8. `DocKind` - 25 edges
9. `build_deps()` - 25 edges
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
- `M3 — Ingestion worker (Days 5–6)` --references--> `EmbeddingProvider`  [INFERRED]
  SPEC.md → backend/app/services/embeddings.py

## Import Cycles
- None detected.

## Communities (65 total, 28 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "Hit"
Cohesion: 0.13
Nodes (10): Hit, FakeReranker, FlashRankReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.13
Nodes (17): EmbeddingError, FakeEmbeddingProvider, is_retryable(), embed(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is() (+9 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "ingestion.py"
Cohesion: 0.05
Nodes (40): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, Base (+32 more)

### Community 6 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (28): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), list_documents() (+20 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (69): chunk_pages(), TextChunk, extract_pages(), PermanentError, put_pdf(), backfill(), Deps, process_one() (+61 more)

### Community 19 - "runner.py"
Cohesion: 0.12
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.15
Nodes (13): keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input() (+5 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "get_settings"
Cohesion: 0.11
Nodes (14): _run(), _run_online(), get_settings(), model_chain_names(), Settings, make_client(), main(), _main() (+6 more)

### Community 24 - "tools.py"
Cohesion: 0.15
Nodes (3): Tool, EmbeddingProvider, call_with_retry()

### Community 25 - "test_agent_loop.py"
Cohesion: 0.06
Nodes (65): call(), clean_schema(), FakeLLM, LLM, LLMError, LLMResponse, Message, parse_response() (+57 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.09
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "invoices_tool"
Cohesion: 0.12
Nodes (14): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+6 more)

### Community 29 - "explain_search.py"
Cohesion: 0.15
Nodes (9): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+1 more)

### Community 30 - "InvoiceFields"
Cohesion: 0.07
Nodes (25): InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason(), _to_fields(), extractor(), invoice() (+17 more)

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 37 - "ModelChain"
Cohesion: 0.12
Nodes (7): GeminiLLM, GeminiInvoiceExtractor, ModelChain, Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "worker/deps.py"
Cohesion: 0.21
Nodes (6): make_engine(), create_app(), lifespan(), FakeInvoiceExtractor, make_s3(), deps()

### Community 44 - "tests/conftest.py"
Cohesion: 0.11
Nodes (10): _db_ok(), health(), s3_ok(), client(), configured(), pg(), s3(), sql() (+2 more)

### Community 45 - "evaluate"
Cohesion: 0.19
Nodes (10): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), evaluate() (+2 more)

### Community 50 - "test_migrations.py"
Cohesion: 0.18
Nodes (6): _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips(), list_models(), main(), probe()

### Community 52 - "test_agent_evals.py"
Cohesion: 0.17
Nodes (15): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes() (+7 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 54 - "test_eval_harness.py"
Cohesion: 0.22
Nodes (7): test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_precomputed_embedder_returns_the_stored_vectors(), append_docs_row(), _load(), precompute()

### Community 56 - "eval_settings"
Cohesion: 0.32
Nodes (5): test_eval_queries_are_never_throttled(), main(), _main(), eval_settings(), _git_sha()

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.21
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 60 - "build_questions.py"
Cohesion: 0.31
Nodes (8): _date(), _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "test_build_questions.py"
Cohesion: 0.24
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 62 - "chunks.py"
Cohesion: 0.31
Nodes (4): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search()

## Knowledge Gaps
- **54 isolated node(s):** `Reproduce`, `Agent evals (M6)`, `Agent answers`, `Major decisions`, `Roadblocks` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 335 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `ingestion.py`, `worker/deps.py`, `runner.py`, `test_agent_evals.py`, `test_search_modes.py`, `test_eval_harness.py`, `get_settings`, `tools.py`, `test_agent_loop.py`, `InvoiceFields`?**
  _High betweenness centrality (0.089) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `ingestion.py`, `test_auth.py`, `api/auth.py`, `worker/deps.py`, `tests/conftest.py`, `test_migrations.py`, `runner.py`, `test_eval_harness.py`, `eval_settings`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `Throttle` connect `ModelChain` to `tools.py`, `worker/deps.py`, `get_settings`, `GeminiEmbeddingProvider`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 96 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 96 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Reproduce`, `Agent evals (M6)`, `Agent answers` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `Hit` be split into smaller, more focused modules?**
  _Cohesion score 0.12615384615384614 - nodes in this community are weakly interconnected._