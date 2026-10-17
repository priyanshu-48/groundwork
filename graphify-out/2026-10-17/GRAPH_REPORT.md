# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 210 files · ~101,538 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 8, .jsonl 2, .example 1)

## Summary
- 1765 nodes · 4941 edges · 118 communities (70 shown, 48 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `e0f46565`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_observability.py
- llm.py
- Groundwork: instructions for Claude Code
- embeddings.py
- relevant_snippet
- sqlalchemy
- test_contract_extraction.py
- test_scoring.py
- datetime
- 0001-local-s3-rustfs.md
- new_org
- groundwork
- api/documents.py
- runner.py
- 0002-approximate-token-counts.md
- typing
- test_model_chain.py
- client.ts
- api/auth.py
- test_agent_loop.py
- generate_corpus.py
- GeminiLLM
- tools.py
- test_eval_harness.py
- llm_with
- test_agent_evals.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- InvoiceFields
- ModelChain
- k6_search.js
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- worker/deps.py
- tests/conftest.py
- invoices.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- Groundwork: Build Spec
- run_evals.py
- test_documents.py
- test_auth.py
- test_search_modes.py
- extraction.py
- loop.py
- LLMResponse
- auth.tsx
- test_extract_many.py
- types.ts
- chunks.py
- lib.sh
- Deploying Groundwork to AWS (CloudShell runbook)
- chat.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- DocumentsPage.tsx
- Document
- LLMUnavailable
- Moving from AWS to Oracle Cloud (free tier)
- Message
- 03-set-secrets.sh
- compilerOptions
- ingestion.py
- Architecture
- Observability (M8)
- check_extraction.py
- Throttle
- Deps
- ChatPage.test.tsx
- storage.py
- PrecomputedEmbedder
- 0013-query-embedding-cache.md
- README.md
- ChatPage.tsx
- InvoiceExtractor
- upload-ask-cite.spec.ts
- test_rrf.py
- test_contracts.py
- Reranker
- instance-setup.sh
- run_agent_evals.py
- restore.sh
- Hit
- chunk_pages
- test_backfill.py
- 01-preflight.sh
- scripts
- 02-create-infra.sh
- 04-deploy.sh
- 99-teardown.sh
- show-secret.sh
- start.sh
- stop.sh
- backup.sh
- fetch-env.sh
- release.sh
- 0014-single-host-deploy-portable-to-oracle.md
- 0015-bundle-deploys-over-ssm.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 140 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 46 edges
4. `Message` - 38 edges
5. `seed()` - 38 edges
6. `process_one()` - 34 edges
7. `build_deps()` - 32 edges
8. `DocKind` - 31 edges
9. `FakeLLM` - 30 edges
10. `search_documents()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M8 — Hardening + observability (Day 16)` --references--> `chat()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py

## Import Cycles
- None detected.

## Communities (118 total, 48 thin omitted)

### Community 0 - "test_observability.py"
Cohesion: 0.06
Nodes (57): clean_request_id(), JsonFormatter, send_with_id(), ConcurrencyLimiter, SlidingWindowLimiter, chat(), ingest(), _ingest() (+49 more)

### Community 1 - "llm.py"
Cohesion: 0.16
Nodes (14): assemble_stream(), clean_schema(), LLMError, parse_response(), _to_content(), ToolCall, ToolResult, specs() (+6 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "embeddings.py"
Cohesion: 0.06
Nodes (29): CachedEmbedder, EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), embed() (+21 more)

### Community 4 - "relevant_snippet"
Cohesion: 0.14
Nodes (10): relevant_snippet(), test_falls_back_to_the_opening_when_nothing_matches(), test_is_capped_and_never_empty(), test_picks_the_sentence_that_supports_the_answer_not_the_opening(), test_short_chunks_are_returned_whole(), 0012: In-memory rate limits and a static admin token, AWS resources (M9), Groundwork journal (interview reference) (+2 more)

### Community 5 - "sqlalchemy"
Cohesion: 0.07
Nodes (26): _base(), upgrade(), create(), history(), list_(), AgentRun, AgentStep, Conversation (+18 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.25
Nodes (13): contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model(), test_documents_are_wrapped_numbered_and_capped() (+5 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "datetime"
Cohesion: 0.15
Nodes (14): current_user(), _unauthorized(), create_token(), decode_token(), hash_password(), TokenError, verify_password(), test_alg_none_rejected() (+6 more)

### Community 12 - "new_org"
Cohesion: 0.15
Nodes (34): process_one(), run_worker(), invoice_text(), make_due(), make_pdf(), new_org(), rows(), scalar() (+26 more)

### Community 17 - "api/documents.py"
Cohesion: 0.08
Nodes (9): ConversationIn, ConversationOut, MessageOut, get_session(), list_documents(), _read_pdf(), upload(), DocumentOut (+1 more)

### Community 19 - "runner.py"
Cohesion: 0.12
Nodes (17): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), _run_job() (+9 more)

### Community 21 - "typing"
Cohesion: 0.08
Nodes (10): metrics(), agent_stats(), HttpMetrics, parse_prices(), percentile(), queue_stats(), test_percentile_interpolates(), test_prices_parse_to_decimal_and_empty_means_none() (+2 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.14
Nodes (18): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+10 more)

### Community 23 - "client.ts"
Cohesion: 0.33
Nodes (14): ApiError, createConversation(), errorMessage(), getMessages(), json(), listConversations(), listDocuments(), login() (+6 more)

### Community 24 - "api/auth.py"
Cohesion: 0.17
Nodes (11): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+3 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.20
Nodes (27): call(), FakeLLM, say(), Usage, execute(), new_org_user(), corpus(), ctx_for() (+19 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (36): small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt(), qs() (+28 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (18): _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryContractsArgs (+10 more)

### Community 29 - "test_eval_harness.py"
Cohesion: 0.18
Nodes (11): ingest_corpus(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task() (+3 more)

### Community 30 - "llm_with"
Cohesion: 0.29
Nodes (6): llm_with(), response(), StubModels, test_generate_disables_auto_function_calling_and_declares_tools(), test_generate_falls_over_to_the_next_model_and_reports_it(), test_generate_raises_clearly_when_every_model_is_exhausted()

### Community 31 - "test_agent_evals.py"
Cohesion: 0.20
Nodes (11): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+3 more)

### Community 33 - "Evaluation results"
Cohesion: 0.33
Nodes (5): Agent answers, Agent evals (M6), Evaluation results, Load tests (M8), Reproduce

### Community 36 - "InvoiceFields"
Cohesion: 0.15
Nodes (14): FakeInvoiceExtractor, InvoiceFields, review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines() (+6 more)

### Community 38 - "k6_search.js"
Cohesion: 0.14
Nodes (10): JSON_H, LIMIT, options, VUS, cold(), options, QUERIES, search() (+2 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "worker/deps.py"
Cohesion: 0.08
Nodes (24): _run(), _run_online(), get_settings(), model_chain_names(), Settings, make_engine(), configure_logging(), RequestContextMiddleware (+16 more)

### Community 44 - "tests/conftest.py"
Cohesion: 0.12
Nodes (10): client(), configured(), pg(), s3(), sql(), run(), go(), _create_db() (+2 more)

### Community 45 - "invoices.py"
Cohesion: 0.19
Nodes (6): delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern()

### Community 50 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 52 - "run_evals.py"
Cohesion: 0.13
Nodes (13): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), append_docs_row() (+5 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 54 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 55 - "test_search_modes.py"
Cohesion: 0.16
Nodes (14): DocKind, keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+6 more)

### Community 56 - "extraction.py"
Cohesion: 0.12
Nodes (11): ContractFields, fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields(), _date(), _LLMInvoice (+3 more)

### Community 57 - "loop.py"
Cohesion: 0.18
Nodes (10): LLM, AgentEvent, run_agent(), _step_limit_answer(), validate_citations(), ask(), ConversationNotFound, make_context() (+2 more)

### Community 58 - "LLMResponse"
Cohesion: 0.18
Nodes (5): DemoLLM, LLMResponse, ToolSpec, 0011: Chat streaming and frontend design, CountingLLM

### Community 59 - "auth.tsx"
Cohesion: 0.19
Nodes (18): getMeta(), setUnauthorizedHandler(), tokenStore, App(), AuthContext, AuthProvider(), AuthValue, RequireAuth() (+10 more)

### Community 60 - "test_extract_many.py"
Cohesion: 0.35
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 61 - "types.ts"
Cohesion: 0.12
Nodes (20): chatEvents(), KNOWN, parseSSE(), RawSSE, enc, toEvent(), toStreamEvent(), ChatMode (+12 more)

### Community 62 - "chunks.py"
Cohesion: 0.19
Nodes (6): Chunk, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 63 - "lib.sh"
Cohesion: 0.27
Nodes (5): aws_(), die(), need_state(), require_cloudshell_ready(), lib.sh script

### Community 64 - "Deploying Groundwork to AWS (CloudShell runbook)"
Cohesion: 0.20
Nodes (9): 1. Get the code into CloudShell, 2. Create, configure, deploy, 3. Check it works, Day to day, Deploying Groundwork to AWS (CloudShell runbook), Local dry run (no AWS), One-time checks (console), Restore drill (do it once) (+1 more)

### Community 65 - "chat.py"
Cohesion: 0.11
Nodes (13): snippet(), MessageIn, send(), stream(), sse(), search(), SearchHit, SearchIn (+5 more)

### Community 66 - "devDependencies"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+12 more)

### Community 67 - "package.json"
Cohesion: 0.08
Nodes (27): dependencies, react, react-dom, react-router-dom, @tanstack/react-query, name, private, type (+19 more)

### Community 72 - "DocumentsPage.tsx"
Cohesion: 0.25
Nodes (9): DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval(), MAX_UPLOAD_BYTES, validateUpload(), DocumentsPage(), api (+1 more)

### Community 73 - "Document"
Cohesion: 0.44
Nodes (4): Document, create_with_job(), get_by_sha(), list_for_org()

### Community 74 - "LLMUnavailable"
Cohesion: 0.33
Nodes (4): LLMUnavailable, generate(), generate(), generate_stream()

### Community 75 - "Moving from AWS to Oracle Cloud (free tier)"
Cohesion: 0.33
Nodes (5): AWS-specific vs portable, Moving from AWS to Oracle Cloud (free tier), Order of operations, What changes (checklist), What stays exactly the same

### Community 76 - "Message"
Cohesion: 0.35
Nodes (11): Message, chunk(), collect(), llm(), StreamModels, test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model(), test_an_empty_stream_is_an_llm_error(), test_bad_requests_do_not_fall_over_and_exhaustion_is_clear() (+3 more)

### Community 77 - "03-set-secrets.sh"
Cohesion: 0.90
Nodes (4): exists(), generate(), put(), 03-set-secrets.sh script

### Community 78 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 79 - "ingestion.py"
Cohesion: 0.11
Nodes (18): Contract, DocStatus, Invoice, review_contract(), ingest_document(), mark_failed(), store_contract(), _store_contract() (+10 more)

### Community 80 - "Architecture"
Cohesion: 0.40
Nodes (4): Architecture, Deployed (M9): one Docker host, AWS now, Oracle later, Local development, Request path (chat)

### Community 81 - "Observability (M8)"
Cohesion: 0.33
Nodes (5): Cost, GET /admin/metrics, Limits (per API process), Logs, Observability (M8)

### Community 82 - "check_extraction.py"
Cohesion: 0.06
Nodes (25): call(), main(), multipart(), step(), _d(), main(), _main(), _print() (+17 more)

### Community 83 - "Throttle"
Cohesion: 0.16
Nodes (5): GeminiInvoiceExtractor, Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 84 - "Deps"
Cohesion: 0.34
Nodes (13): Deps, ctx_for(), org(), q(), test_another_org_sees_none_of_it(), test_bad_arguments_come_back_as_errors_the_model_can_fix(), test_date_range_is_inclusive_on_both_ends(), test_flagged_invoices_never_count() (+5 more)

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.25
Nodes (6): ChatMessage, api, cite, enc, renderChat(), stored

### Community 86 - "storage.py"
Cohesion: 0.23
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 91 - "ChatPage.tsx"
Cohesion: 0.21
Nodes (11): Citation, CitationDetail(), CitedText(), Props, Segment, splitCitations(), LABEL, StepsPanel() (+3 more)

### Community 94 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 97 - "test_contracts.py"
Cohesion: 0.29
Nodes (11): add_invoice_row(), add_contract(), ctx_for(), org(), q(), test_invoices_can_be_filtered_by_the_vendors_contract_terms(), test_multi_hop_is_now_two_tool_calls_not_a_search_loop(), test_query_contracts_filters_by_terms_renewal_and_law() (+3 more)

### Community 100 - "run_agent_evals.py"
Cohesion: 0.20
Nodes (10): test_eval_queries_are_never_throttled(), append_agent_rows(), _append_cache(), ask_once(), evaluate_agent(), load_cache(), main(), _main() (+2 more)

### Community 102 - "Hit"
Cohesion: 0.13
Nodes (10): Hit, FakeReranker, FlashRankReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 103 - "chunk_pages"
Cohesion: 0.39
Nodes (10): chunk_pages(), words(), test_blank_pages_are_skipped_but_page_numbers_stay_true(), test_consecutive_chunks_overlap_and_respect_size(), test_default_window_is_about_500_tokens_with_60_overlap(), test_deterministic(), test_never_crosses_a_page_boundary(), test_newlines_are_preserved() (+2 more)

### Community 104 - "test_backfill.py"
Cohesion: 0.38
Nodes (8): backfill(), BackfillResult, CountingExtractor, ingest_without_extraction(), test_backfill_extracts_ten_per_call_flags_bad_totals_and_is_idempotent(), test_backfill_ignores_contracts_and_documents_still_processing(), test_backfill_limit_stops_early_and_resumes(), test_retry_flagged_reextracts_once_per_run_without_looping()

### Community 106 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, lint, preview, test, test:watch (+1 more)

## Knowledge Gaps
- **171 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `01-preflight.sh script`, `02-create-infra.sh script` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 588 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **48 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `chat.py`, `test_contracts.py`, `embeddings.py`, `run_agent_evals.py`, `test_backfill.py`, `worker/deps.py`, `new_org`, `ingestion.py`, `runner.py`, `test_search_modes.py`, `loop.py`, `InvoiceExtractor`, `test_eval_harness.py`, `test_agent_loop.py`, `test_agent_evals.py`?**
  _High betweenness centrality (0.070) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `worker/deps.py` to `test_observability.py`, `run_agent_evals.py`, `datetime`, `tests/conftest.py`, `ingestion.py`, `api/documents.py`, `check_extraction.py`, `runner.py`, `typing`, `storage.py`, `test_auth.py`, `api/auth.py`, `test_eval_harness.py`?**
  _High betweenness centrality (0.035) - this node is a cross-community bridge._
- **Why does `upload()` connect `api/documents.py` to `chat.py`, `worker/deps.py`, `test_search_modes.py`?**
  _High betweenness centrality (0.019) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 118 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _171 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_observability.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05709507883420927 - nodes in this community are weakly interconnected._
- **Should `embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.059395801331285206 - nodes in this community are weakly interconnected._