# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 131 files · ~74,573 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1242 nodes · 3600 edges · 77 communities (46 shown, 31 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 225 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `bf8311d1`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- Hit
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- sqlalchemy
- test_contract_extraction.py
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- test_agent_loop.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- extraction.py
- worker/deps.py
- llm.py
- generate_corpus.py
- test_rrf.py
- tools.py
- run_evals.py
- test_extraction.py
- run_agent_evals.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- InvoiceFields
- LLMUnavailable
- test_agent_evals.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- get_settings
- tests/conftest.py
- ingestion.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- backfill_contracts.py
- test_eval_harness.py
- test_documents.py
- test_extract_many.py
- GeminiInvoiceExtractor
- loop.py
- percentile
- test_build_retrieval_questions.py
- build_ground_truth
- build_questions.py
- pytest
- chunks.py
- check_extraction.py
- typing
- ContractFields
- small
- explain_search.py
- CountingLLM
- PrecomputedEmbedder
- 0010-structured-contract-facts.md
- FakeInvoiceExtractor

## God Nodes (most connected - your core abstractions)
1. `Deps` - 107 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 38 edges
4. `process_one()` - 35 edges
5. `seed()` - 35 edges
6. `search_documents()` - 28 edges
7. `build_deps()` - 28 edges
8. `make_pdf()` - 27 edges
9. `DocKind` - 26 edges
10. `Hit` - 23 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
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

## Communities (77 total, 31 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "Hit"
Cohesion: 0.12
Nodes (11): Hit, FakeReranker, FlashRankReranker, Reranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.10
Nodes (18): EmbeddingError, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), embed(), _cos(), _provider() (+10 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.06
Nodes (30): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, Base (+22 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.20
Nodes (15): review_contract(), contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model() (+7 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (39): login(), me(), signup(), _token(), current_user(), _unauthorized(), list_documents(), _read_pdf() (+31 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (84): chunk_pages(), put_pdf(), backfill(), Deps, process_one(), run_worker(), add_invoice_row(), ingest_corpus() (+76 more)

### Community 17 - "test_agent_loop.py"
Cohesion: 0.25
Nodes (25): call(), FakeLLM, say(), Usage, execute(), new_org_user(), ctx_for(), drain() (+17 more)

### Community 19 - "test_queue.py"
Cohesion: 0.14
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.15
Nodes (14): DocKind, keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+6 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "extraction.py"
Cohesion: 0.20
Nodes (6): fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields(), _money()

### Community 24 - "worker/deps.py"
Cohesion: 0.12
Nodes (12): model_chain_names(), Settings, EmbeddingProvider, make_client(), Throttle, main(), _main(), build_deps() (+4 more)

### Community 25 - "llm.py"
Cohesion: 0.11
Nodes (23): clean_schema(), GeminiLLM, LLMResponse, Message, parse_response(), _to_content(), ToolCall, ToolResult (+15 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.14
Nodes (11): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+3 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.11
Nodes (19): AgentContext, _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable() (+11 more)

### Community 29 - "run_evals.py"
Cohesion: 0.11
Nodes (9): _auth(), main(), _main(), _retry(), _statuses(), _upload(), list_models(), main() (+1 more)

### Community 30 - "test_extraction.py"
Cohesion: 0.23
Nodes (12): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero() (+4 more)

### Community 32 - "run_agent_evals.py"
Cohesion: 0.15
Nodes (11): test_cache_keys_change_with_the_model_chain_and_search_mode(), append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache(), main() (+3 more)

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "InvoiceFields"
Cohesion: 0.14
Nodes (3): InvoiceExtractor, InvoiceFields, _LLMInvoice

### Community 37 - "LLMUnavailable"
Cohesion: 0.13
Nodes (4): call_with_retry(), LLMUnavailable, test_model_outage_ends_the_run_cleanly(), generate()

### Community 38 - "test_agent_evals.py"
Cohesion: 0.29
Nodes (8): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "get_settings"
Cohesion: 0.16
Nodes (12): _run(), _run_online(), get_settings(), make_engine(), lifespan(), make_s3(), go(), deps() (+4 more)

### Community 44 - "tests/conftest.py"
Cohesion: 0.13
Nodes (10): create_app(), client(), configured(), pg(), s3(), sql(), run(), _create_db() (+2 more)

### Community 45 - "ingestion.py"
Cohesion: 0.07
Nodes (16): Contract, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern(), ingest_document() (+8 more)

### Community 50 - "backfill_contracts.py"
Cohesion: 0.24
Nodes (5): backfill(), BackfillResult, main(), _main(), _next_batch()

### Community 52 - "test_eval_harness.py"
Cohesion: 0.13
Nodes (13): test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), append_docs_row(), eval_settings() (+5 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 54 - "test_extract_many.py"
Cohesion: 0.31
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 56 - "loop.py"
Cohesion: 0.14
Nodes (12): LLM, LLMError, AgentEvent, run_agent(), snippet(), _step_limit_answer(), validate_citations(), ask() (+4 more)

### Community 57 - "percentile"
Cohesion: 0.29
Nodes (7): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k()

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.24
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 59 - "build_ground_truth"
Cohesion: 0.26
Nodes (8): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth()

### Community 60 - "build_questions.py"
Cohesion: 0.31
Nodes (8): _date(), _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "pytest"
Cohesion: 0.20
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 62 - "chunks.py"
Cohesion: 0.20
Nodes (5): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 63 - "check_extraction.py"
Cohesion: 0.36
Nodes (6): _d(), main(), _main(), _print(), score_contracts(), score_invoices()

### Community 64 - "typing"
Cohesion: 0.13
Nodes (4): get_session(), _db_ok(), health(), s3_ok()

### Community 67 - "explain_search.py"
Cohesion: 0.43
Nodes (3): _explain(), main(), _vec()

## Knowledge Gaps
- **55 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 379 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `InvoiceFields`, `sqlalchemy`, `test_agent_evals.py`, `LLMUnavailable`, `get_settings`, `ingestion.py`, `test_agent_loop.py`, `backfill_contracts.py`, `test_eval_harness.py`, `test_search_modes.py`, `loop.py`, `worker/deps.py`?**
  _High betweenness centrality (0.068) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `typing`, `sqlalchemy`, `api/auth.py`, `tests/conftest.py`, `ingestion.py`, `backfill_contracts.py`, `test_queue.py`, `test_eval_harness.py`, `worker/deps.py`, `check_extraction.py`?**
  _High betweenness centrality (0.040) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `Groundwork: Build Spec` to `api/auth.py`?**
  _High betweenness centrality (0.033) - this node is a cross-community bridge._
- **Are the 87 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 87 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `Hit` be split into smaller, more focused modules?**
  _Cohesion score 0.1225071225071225 - nodes in this community are weakly interconnected._