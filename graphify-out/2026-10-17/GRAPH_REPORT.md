# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 188 files · ~94,582 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 7, .jsonl 2, .example 1)

## Summary
- 1695 nodes · 4830 edges · 113 communities (74 shown, 39 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e0f46565`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_observability.py
- llm.py
- Groundwork: instructions for Claude Code
- FakeEmbeddingProvider
- SlidingWindowLimiter
- sqlalchemy
- test_contract_extraction.py
- test_scoring.py
- security.py
- 0001-local-s3-rustfs.md
- seed
- groundwork
- upload
- test_queue.py
- 0002-approximate-token-counts.md
- services/metrics.py
- test_model_chain.py
- service.py
- api/auth.py
- test_agent_loop.py
- generate_corpus.py
- send
- tools.py
- new_org
- 0004_chunks_invoices.py
- test_agent_evals.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- test_extraction.py
- ModelChain
- k6_search.js
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- get_settings
- asyncio
- Contract
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- Groundwork: Build Spec
- evaluate
- test_documents.py
- test_auth.py
- test_search_modes.py
- contract_extraction.py
- loop.py
- LLMResponse
- client.ts
- test_extract_many.py
- sse.ts
- chunks.py
- search.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- types.ts
- DocKind
- worker/deps.py
- api/deps.py
- Message
- CachedEmbedder
- compilerOptions
- ingestion.py
- typing
- Observability (M8)
- check_extraction.py
- GeminiInvoiceExtractor
- Deps
- ChatPage.test.tsx
- health.py
- run_evals.py
- 0013-query-embedding-cache.md
- README.md
- main.py
- ChatPage.tsx
- InvoiceFields
- upload-ask-cite.spec.ts
- pytest
- test_contracts.py
- Hit
- runner.py
- run_agent_evals.py
- login
- test_rerank.py
- chunk_pages
- test_backfill.py
- _main
- scripts
- list_

## God Nodes (most connected - your core abstractions)
1. `Deps` - 135 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 43 edges
4. `Message` - 38 edges
5. `seed()` - 38 edges
6. `process_one()` - 34 edges
7. `build_deps()` - 32 edges
8. `DocKind` - 31 edges
9. `FakeLLM` - 30 edges
10. `make_pdf()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `M8 — Hardening + observability (Day 16)` --references--> `chat()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py

## Import Cycles
- None detected.

## Communities (113 total, 39 thin omitted)

### Community 0 - "test_observability.py"
Cohesion: 0.18
Nodes (34): say(), chat(), ingest(), _ingest(), new_conv(), parse_sse(), ref_in(), set_llm() (+26 more)

### Community 1 - "llm.py"
Cohesion: 0.09
Nodes (21): assemble_stream(), clean_schema(), GeminiLLM, LLMError, parse_response(), _to_content(), ToolCall, ToolResult (+13 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "FakeEmbeddingProvider"
Cohesion: 0.10
Nodes (18): EmbeddingError, FakeEmbeddingProvider, _normalize(), is_retryable(), embed(), Recording, _cos(), _provider() (+10 more)

### Community 4 - "SlidingWindowLimiter"
Cohesion: 0.09
Nodes (19): relevant_snippet(), ConcurrencyLimiter, SlidingWindowLimiter, Clock, test_a_leaked_slot_is_reclaimed_after_the_max_hold(), test_allows_up_to_the_limit_then_reports_when_to_retry(), test_concurrency_cap_release_and_idempotent_release(), test_idle_keys_are_pruned() (+11 more)

### Community 5 - "sqlalchemy"
Cohesion: 0.24
Nodes (9): Base, IdMixin, Chunk, Job, JobStatus, Org, User, create_org_with_user() (+1 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.20
Nodes (15): review_contract(), contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model() (+7 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "security.py"
Cohesion: 0.22
Nodes (12): create_token(), decode_token(), hash_password(), TokenError, verify_password(), test_alg_none_rejected(), test_expired_token_rejected(), test_missing_org_claim_rejected() (+4 more)

### Community 12 - "seed"
Cohesion: 0.16
Nodes (30): extract_pages(), process_one(), invoice_text(), make_due(), make_pdf(), rows(), scalar(), seed() (+22 more)

### Community 17 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 19 - "test_queue.py"
Cohesion: 0.15
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "services/metrics.py"
Cohesion: 0.12
Nodes (10): metrics(), agent_stats(), HttpMetrics, parse_prices(), percentile(), queue_stats(), test_percentile_interpolates(), test_prices_parse_to_decimal_and_empty_means_none() (+2 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.14
Nodes (18): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+10 more)

### Community 23 - "service.py"
Cohesion: 0.17
Nodes (17): ask(), ConversationNotFound, make_context(), history(), AgentRun, AgentStep, Conversation, Message (+9 more)

### Community 24 - "api/auth.py"
Cohesion: 0.22
Nodes (7): me(), _token(), _EmailIn, LoginIn, MeOut, SignupIn, TokenOut

### Community 25 - "test_agent_loop.py"
Cohesion: 0.19
Nodes (24): FakeLLM, execute(), new_org_user(), ctx_for(), drain(), last_ref(), run(), test_a_hallucinated_citation_is_dropped_and_counted() (+16 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (37): _date(), small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt() (+29 more)

### Community 27 - "send"
Cohesion: 0.07
Nodes (13): MessageIn, send(), stream(), sse(), clean_request_id(), JsonFormatter, send_with_id(), Grab (+5 more)

### Community 28 - "tools.py"
Cohesion: 0.10
Nodes (19): _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryContractsArgs (+11 more)

### Community 29 - "new_org"
Cohesion: 0.16
Nodes (14): put_pdf(), ingest_corpus(), new_org(), corpus(), test_generated_corpus_ingests_with_every_fact_right(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too() (+6 more)

### Community 31 - "test_agent_evals.py"
Cohesion: 0.27
Nodes (8): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes()

### Community 33 - "Evaluation results"
Cohesion: 0.33
Nodes (5): Agent answers, Agent evals (M6), Evaluation results, Load tests (M8), Reproduce

### Community 36 - "test_extraction.py"
Cohesion: 0.26
Nodes (11): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero(), test_money_parsing_tolerates_formats_models_produce() (+3 more)

### Community 37 - "ModelChain"
Cohesion: 0.15
Nodes (6): LLMUnavailable, ModelChain, generate(), generate(), generate_stream(), test_empty_chain_is_rejected()

### Community 38 - "k6_search.js"
Cohesion: 0.14
Nodes (10): JSON_H, LIMIT, options, VUS, cold(), options, QUERIES, search() (+2 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "get_settings"
Cohesion: 0.17
Nodes (11): _run(), _run_online(), get_settings(), make_engine(), go(), deps(), test_health_degraded_when_s3_missing(), test_health_ok() (+3 more)

### Community 44 - "asyncio"
Cohesion: 0.09
Nodes (11): configured(), pg(), s3(), sql(), run(), _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips() (+3 more)

### Community 45 - "Contract"
Cohesion: 0.19
Nodes (8): Contract, Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern()

### Community 50 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (32): step(), 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture (+24 more)

### Community 52 - "evaluate"
Cohesion: 0.23
Nodes (8): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), evaluate()

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 54 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 55 - "test_search_modes.py"
Cohesion: 0.16
Nodes (13): keyword_search(), search_documents(), corpus(), test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input() (+5 more)

### Community 56 - "contract_extraction.py"
Cohesion: 0.23
Nodes (6): fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields(), _money()

### Community 57 - "loop.py"
Cohesion: 0.28
Nodes (7): Usage, AgentEvent, run_agent(), _step_limit_answer(), validate_citations(), AgentContext, specs()

### Community 58 - "LLMResponse"
Cohesion: 0.16
Nodes (7): DemoLLM, call(), LLM, LLMResponse, ToolSpec, 0011: Chat streaming and frontend design, CountingLLM

### Community 59 - "client.ts"
Cohesion: 0.14
Nodes (30): ApiError, createConversation(), errorMessage(), getMessages(), getMeta(), json(), listConversations(), listDocuments() (+22 more)

### Community 60 - "test_extract_many.py"
Cohesion: 0.31
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 61 - "sse.ts"
Cohesion: 0.29
Nodes (7): chatEvents(), KNOWN, parseSSE(), RawSSE, enc, toEvent(), toStreamEvent()

### Community 62 - "chunks.py"
Cohesion: 0.24
Nodes (5): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 65 - "search.py"
Cohesion: 0.26
Nodes (7): snippet(), search(), SearchHit, SearchIn, SearchOut, get_limits(), Limits

### Community 66 - "devDependencies"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+12 more)

### Community 67 - "package.json"
Cohesion: 0.08
Nodes (26): dependencies, react, react-dom, react-router-dom, @tanstack/react-query, name, private, type (+18 more)

### Community 72 - "types.ts"
Cohesion: 0.20
Nodes (13): ChatMode, Conversation, DocKind, DocStatus, DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval() (+5 more)

### Community 73 - "DocKind"
Cohesion: 0.17
Nodes (9): DocKind, DocStatus, Document, create_with_job(), get_by_sha(), list_for_org(), DocumentOut, _next_batch() (+1 more)

### Community 74 - "worker/deps.py"
Cohesion: 0.08
Nodes (18): model_chain_names(), Settings, EmbeddingProvider, GeminiEmbeddingProvider, make_client(), Throttle, make_s3(), backfill() (+10 more)

### Community 75 - "api/deps.py"
Cohesion: 0.15
Nodes (5): current_user(), get_session(), _unauthorized(), Principal, M1 — Auth + tenancy (Day 2)

### Community 76 - "Message"
Cohesion: 0.35
Nodes (11): Message, chunk(), collect(), llm(), StreamModels, test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model(), test_an_empty_stream_is_an_llm_error(), test_bad_requests_do_not_fall_over_and_exhaustion_is_clear() (+3 more)

### Community 77 - "CachedEmbedder"
Cohesion: 0.18
Nodes (8): CachedEmbedder, Counting, test_concurrent_identical_queries_share_one_call(), test_documents_are_never_cached(), test_failures_are_not_cached(), embed(), test_least_recently_used_entry_is_evicted(), test_repeated_query_is_embedded_once()

### Community 78 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 79 - "ingestion.py"
Cohesion: 0.15
Nodes (10): ContractFields, ingest_document(), mark_failed(), store_contract(), _store_contract(), store_invoice(), _store_invoice(), get_bytes() (+2 more)

### Community 80 - "typing"
Cohesion: 0.10
Nodes (6): ConversationIn, ConversationOut, MessageOut, list_models(), main(), probe()

### Community 81 - "Observability (M8)"
Cohesion: 0.33
Nodes (5): Cost, GET /admin/metrics, Limits (per API process), Logs, Observability (M8)

### Community 82 - "check_extraction.py"
Cohesion: 0.10
Nodes (15): _d(), main(), _main(), _print(), score_contracts(), score_invoices(), _auth(), main() (+7 more)

### Community 84 - "Deps"
Cohesion: 0.34
Nodes (13): Deps, ctx_for(), org(), q(), test_another_org_sees_none_of_it(), test_bad_arguments_come_back_as_errors_the_model_can_fix(), test_date_range_is_inclusive_on_both_ends(), test_flagged_invoices_never_count() (+5 more)

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.25
Nodes (6): ChatMessage, api, cite, enc, stored, @testing-library/user-event

### Community 86 - "health.py"
Cohesion: 0.36
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 90 - "main.py"
Cohesion: 0.12
Nodes (7): configure_logging(), RequestContextMiddleware, create_app(), lifespan(), build_limits(), main(), client()

### Community 91 - "ChatPage.tsx"
Cohesion: 0.14
Nodes (21): Citation, DoneData, StepData, StreamEvent, Action, applyEvent(), idle, reducer() (+13 more)

### Community 92 - "InvoiceFields"
Cohesion: 0.11
Nodes (5): FakeInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, test_fake_extractor_reads_labelled_lines()

### Community 94 - "pytest"
Cohesion: 0.18
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 97 - "test_contracts.py"
Cohesion: 0.29
Nodes (11): add_invoice_row(), add_contract(), ctx_for(), org(), q(), test_invoices_can_be_filtered_by_the_vendors_contract_terms(), test_multi_hop_is_now_two_tool_calls_not_a_search_loop(), test_query_contracts_filters_by_terms_renewal_and_law() (+3 more)

### Community 98 - "Hit"
Cohesion: 0.17
Nodes (5): Hit, FlashRankReranker, RecordingReranker, test_real_model_puts_the_relevant_passage_first(), hit()

### Community 99 - "runner.py"
Cohesion: 0.16
Nodes (4): PermanentError, run_worker(), test_run_worker_drains_the_queue_then_stops_on_signal(), all_ready()

### Community 100 - "run_agent_evals.py"
Cohesion: 0.15
Nodes (13): test_cache_keys_change_with_the_model_chain_and_search_mode(), test_eval_queries_are_never_throttled(), append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache() (+5 more)

### Community 101 - "login"
Cohesion: 0.22
Nodes (4): login(), signup(), client_ip(), too_many()

### Community 102 - "test_rerank.py"
Cohesion: 0.22
Nodes (6): FakeReranker, hit(), StubRanker, test_empty_candidates_skip_the_model(), test_fake_reranker_orders_by_word_overlap_and_caps_top_k(), test_flashrank_adapter_maps_ids_sorts_by_score_and_stays_off_the_loop()

### Community 103 - "chunk_pages"
Cohesion: 0.39
Nodes (10): chunk_pages(), words(), test_blank_pages_are_skipped_but_page_numbers_stay_true(), test_consecutive_chunks_overlap_and_respect_size(), test_default_window_is_about_500_tokens_with_60_overlap(), test_deterministic(), test_never_crosses_a_page_boundary(), test_newlines_are_preserved() (+2 more)

### Community 104 - "test_backfill.py"
Cohesion: 0.53
Nodes (7): backfill(), CountingExtractor, ingest_without_extraction(), test_backfill_extracts_ten_per_call_flags_bad_totals_and_is_idempotent(), test_backfill_ignores_contracts_and_documents_still_processing(), test_backfill_limit_stops_early_and_resumes(), test_retry_flagged_reextracts_once_per_run_without_looping()

### Community 105 - "_main"
Cohesion: 0.28
Nodes (4): append_docs_row(), _load(), main(), _main()

### Community 106 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, lint, preview, test, test:watch (+1 more)

## Knowledge Gaps
- **138 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+133 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 547 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **39 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `step()` connect `Groundwork: Build Spec` to `ChatPage.tsx`?**
  _High betweenness centrality (0.166) - this node is a cross-community bridge._
- **Are the 113 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 113 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _138 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08787878787878788 - nodes in this community are weakly interconnected._
- **Should `FakeEmbeddingProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.0957983193277311 - nodes in this community are weakly interconnected._
- **Should `SlidingWindowLimiter` be split into smaller, more focused modules?**
  _Cohesion score 0.08739495798319327 - nodes in this community are weakly interconnected._
- **Should `test_queue.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14838709677419354 - nodes in this community are weakly interconnected._