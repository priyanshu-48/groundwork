# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 120 files · ~67,865 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1105 nodes · 3160 edges · 77 communities (45 shown, 32 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 231 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a7158628`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- backfill_invoices.py
- runner.py
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- test_gemini_llm.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- get_settings
- FlashRankReranker
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- load_corpus.py
- ingestion.py
- tests/conftest.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- run_agent_evals.py
- upload
- search_documents
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- Message
- api/documents.py
- chunks.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- run_evals.py
- loop.py
- FakeEmbeddingProvider
- test_agent_evals.py
- 8. Milestones (about 3 weeks, one Claude Code session each)
- test_metrics.py
- test_build_retrieval_questions.py
- 6. Key designs (know these well, because they are the interview questions)
- build_questions.py
- test_build_questions.py
- typing
- ModelChain
- probe_models.py
- worker/deps.py
- GeminiEmbeddingProvider
- PrecomputedEmbedder
- is_retryable

## God Nodes (most connected - your core abstractions)
1. `Deps` - 107 edges
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

## Communities (77 total, 32 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.15
Nodes (12): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+4 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.32
Nodes (10): EmbeddingError, embed(), _provider(), StubModels, test_gemini_batches_of_50_and_normalizes(), test_gemini_does_not_retry_client_errors(), test_gemini_gives_up_after_max_tries(), test_gemini_query_task_type() (+2 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "backfill_invoices.py"
Cohesion: 0.05
Nodes (37): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, Base (+29 more)

### Community 6 - "runner.py"
Cohesion: 0.17
Nodes (3): reap_stale(), run_reaper(), main()

### Community 7 - "test_scoring.py"
Cohesion: 0.17
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.07
Nodes (36): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+28 more)

### Community 12 - "Deps"
Cohesion: 0.09
Nodes (57): chunk_pages(), TextChunk, backfill(), Deps, process_one(), run_worker(), invoice_text(), make_due() (+49 more)

### Community 17 - "test_gemini_llm.py"
Cohesion: 0.14
Nodes (16): clean_schema(), GeminiLLM, LLMError, parse_response(), ToolCall, llm_with(), response(), StubModels (+8 more)

### Community 19 - "test_queue.py"
Cohesion: 0.20
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.16
Nodes (12): keyword_search(), corpus(), RecordingReranker, test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input(), test_keyword_uses_or_semantics_so_one_unmatched_word_does_not_zero_the_result() (+4 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "get_settings"
Cohesion: 0.16
Nodes (12): _run(), _run_online(), get_settings(), make_engine(), main(), _main(), run(), go() (+4 more)

### Community 24 - "FlashRankReranker"
Cohesion: 0.17
Nodes (7): FakeReranker, FlashRankReranker, hit(), StubRanker, test_empty_candidates_skip_the_model(), test_fake_reranker_orders_by_word_overlap_and_caps_top_k(), test_flashrank_adapter_maps_ids_sorts_by_score_and_stays_off_the_loop()

### Community 25 - "test_agent_loop.py"
Cohesion: 0.11
Nodes (35): call(), FakeLLM, say(), Usage, AgentEvent, ask(), ConversationNotFound, make_context() (+27 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.09
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (15): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+7 more)

### Community 29 - "load_corpus.py"
Cohesion: 0.24
Nodes (6): _auth(), main(), _main(), _retry(), _statuses(), _upload()

### Community 30 - "ingestion.py"
Cohesion: 0.05
Nodes (33): GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason(), _to_fields(), ingest_document() (+25 more)

### Community 31 - "tests/conftest.py"
Cohesion: 0.14
Nodes (8): client(), configured(), pg(), s3(), sql(), _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips()

### Community 33 - "Evaluation results"
Cohesion: 0.50
Nodes (3): Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "run_agent_evals.py"
Cohesion: 0.14
Nodes (13): test_cache_keys_change_with_the_model_chain_and_search_mode(), test_eval_queries_are_never_throttled(), append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache() (+5 more)

### Community 37 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 38 - "search_documents"
Cohesion: 0.14
Nodes (11): DocKind, search_documents(), ingest_corpus(), test_every_mode_and_set_reports_all_metrics(), test_hard_set_exact_ids_are_found_by_keyword_modes(), Recording, test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task() (+3 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "Message"
Cohesion: 0.25
Nodes (7): LLM, LLMResponse, Message, _to_content(), ToolSpec, test_raw_model_content_is_replayed_verbatim(), CountingLLM

### Community 44 - "api/documents.py"
Cohesion: 0.15
Nodes (6): _db_ok(), health(), create_app(), lifespan(), put_pdf(), s3_ok()

### Community 45 - "chunks.py"
Cohesion: 0.16
Nodes (8): fetch_by_ids(), first_chunks(), Hit, replace_for_document(), vector_search(), Reranker, test_real_model_puts_the_relevant_passage_first(), hit()

### Community 52 - "run_evals.py"
Cohesion: 0.13
Nodes (11): test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_precomputed_embedder_returns_the_stored_vectors(), test_percentile_interpolates(), percentile(), append_docs_row(), evaluate(), _load() (+3 more)

### Community 53 - "loop.py"
Cohesion: 0.24
Nodes (9): ToolResult, run_agent(), snippet(), _step_limit_answer(), validate_citations(), specs(), LLMUnavailable, test_model_outage_ends_the_run_cleanly() (+1 more)

### Community 54 - "FakeEmbeddingProvider"
Cohesion: 0.16
Nodes (7): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), _cos(), test_fake_is_deterministic_768d_and_unit_norm(), test_fake_related_text_scores_higher_than_unrelated(), M3 — Ingestion worker (Days 5–6)

### Community 55 - "test_agent_evals.py"
Cohesion: 0.35
Nodes (7): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes()

### Community 56 - "8. Milestones (about 3 weeks, one Claude Code session each)"
Cohesion: 0.18
Nodes (11): 8. Milestones (about 3 weeks, one Claude Code session each), M0 — Skeleton (Day 1), M10 — Polish for recruiters (Days 20–21), M1 — Auth + tenancy (Day 2), M2 — Upload, S3, idempotency, job queue (Days 3–4), M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8), M5 — Hybrid search + reranking (Days 9–10), M6 — Agent loop + tools + citations (Days 11–12) (+3 more)

### Community 57 - "test_metrics.py"
Cohesion: 0.46
Nodes (5): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), recall_at_k()

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.21
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 59 - "6. Key designs (know these well, because they are the interview questions)"
Cohesion: 0.25
Nodes (8): 6.1 Idempotent upload, 6.2 Job queue with SKIP LOCKED, 6.3 Ingestion pipeline (worker), 6.4 Hybrid retrieval + reranking, 6.5 Agent loop (hand-written), 6.6 Streaming API, 6.7 Multi-tenancy, 6. Key designs (know these well, because they are the interview questions)

### Community 60 - "build_questions.py"
Cohesion: 0.31
Nodes (8): _date(), _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "test_build_questions.py"
Cohesion: 0.22
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 62 - "typing"
Cohesion: 0.15
Nodes (5): call_with_retry(), Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 64 - "probe_models.py"
Cohesion: 0.43
Nodes (3): list_models(), main(), probe()

### Community 65 - "worker/deps.py"
Cohesion: 0.19
Nodes (7): model_chain_names(), Settings, FakeInvoiceExtractor, make_client(), make_s3(), build_deps(), deps()

## Knowledge Gaps
- **53 isolated node(s):** `Reproduce`, `Agent evals (M6)`, `Major decisions`, `Roadblocks`, `Tool` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 337 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **32 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `worker/deps.py`, `run_agent_evals.py`, `backfill_invoices.py`, `runner.py`, `search_documents`, `run_evals.py`, `loop.py`, `FakeEmbeddingProvider`, `test_agent_evals.py`, `test_search_modes.py`, `test_agent_loop.py`, `ingestion.py`?**
  _High betweenness centrality (0.106) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `worker/deps.py`, `run_agent_evals.py`, `backfill_invoices.py`, `upload`, `runner.py`, `api/auth.py`, `api/documents.py`, `test_queue.py`, `run_evals.py`, `tests/conftest.py`?**
  _High betweenness centrality (0.053) - this node is a cross-community bridge._
- **Why does `build_deps()` connect `worker/deps.py` to `GeminiEmbeddingProvider`, `run_agent_evals.py`, `backfill_invoices.py`, `runner.py`, `Deps`, `test_gemini_llm.py`, `run_evals.py`, `FakeEmbeddingProvider`, `get_settings`, `typing`, `FlashRankReranker`, `ingestion.py`, `ModelChain`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 89 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 89 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Reproduce`, `Agent evals (M6)`, `Major decisions` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `backfill_invoices.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05304982817869416 - nodes in this community are weakly interconnected._
- **Should `api/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07242063492063493 - nodes in this community are weakly interconnected._