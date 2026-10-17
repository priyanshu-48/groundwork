# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 210 files · ~101,538 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 16 file(s) not represented in the graph (top: (none) 8, .jsonl 2, .example 1)

## Summary
- 1776 nodes · 4940 edges · 130 communities (75 shown, 55 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 328 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `78ce54ac`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_observability.py
- test_gemini_llm.py
- Groundwork: instructions for Claude Code
- FakeEmbeddingProvider
- relevant_snippet
- sqlalchemy
- test_contract_extraction.py
- test_scoring.py
- security.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- api/documents.py
- test_queue.py
- 0002-approximate-token-counts.md
- HttpMetrics
- test_model_chain.py
- client.ts
- api/auth.py
- test_agent_loop.py
- generate_corpus.py
- worker/deps.py
- tools.py
- test_eval_harness.py
- build_questions.py
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
- tests/conftest.py
- logging.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- Groundwork: Build Spec
- run_evals.py
- test_auth.py
- datetime
- test_search_modes.py
- contract_extraction.py
- loop.py
- LLMResponse
- auth.tsx
- test_extract_many.py
- reducer.ts
- chunks.py
- lib.sh
- Deploying Groundwork to AWS (CloudShell runbook)
- chat.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- types.ts
- DocKind
- run_agent
- Moving from AWS to Oracle Cloud (free tier)
- Message
- 03-set-secrets.sh
- compilerOptions
- ingestion.py
- Architecture
- Observability (M8)
- smoke.py
- GeminiInvoiceExtractor
- json
- ChatPage.test.tsx
- health.py
- PrecomputedEmbedder
- 0013-query-embedding-cache.md
- README.md
- RequestContextMiddleware
- CitedText.test.tsx
- extraction.py
- upload-ask-cite.spec.ts
- test_rrf.py
- pytest
- ContractFields
- instance-setup.sh
- run_agent_evals.py
- restore.sh
- Hit
- admin.py
- main.py
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
- test_build_retrieval_questions.py
- check_extraction.py
- pathlib
- _short

## God Nodes (most connected - your core abstractions)
1. `Deps` - 140 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 46 edges
4. `seed()` - 38 edges
5. `Message` - 37 edges
6. `process_one()` - 34 edges
7. `build_deps()` - 32 edges
8. `DocKind` - 31 edges
9. `FakeLLM` - 30 edges
10. `make_pdf()` - 30 edges

## Surprising Connections (you probably didn't know these)
- `M8 — Hardening + observability (Day 16)` --references--> `chat()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py

## Import Cycles
- None detected.

## Communities (130 total, 55 thin omitted)

### Community 0 - "test_observability.py"
Cohesion: 0.10
Nodes (44): ConcurrencyLimiter, SlidingWindowLimiter, chat(), ingest(), _ingest(), new_conv(), parse_sse(), ref_in() (+36 more)

### Community 1 - "test_gemini_llm.py"
Cohesion: 0.12
Nodes (19): assemble_stream(), clean_schema(), LLMError, parse_response(), _to_content(), ToolCall, specs(), llm_with() (+11 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "FakeEmbeddingProvider"
Cohesion: 0.05
Nodes (30): CachedEmbedder, EmbeddingError, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), Throttle, embed() (+22 more)

### Community 4 - "relevant_snippet"
Cohesion: 0.14
Nodes (10): relevant_snippet(), test_falls_back_to_the_opening_when_nothing_matches(), test_is_capped_and_never_empty(), test_picks_the_sentence_that_supports_the_answer_not_the_opening(), test_short_chunks_are_returned_whole(), 0012: In-memory rate limits and a static admin token, AWS resources (M9), Groundwork journal (interview reference) (+2 more)

### Community 5 - "sqlalchemy"
Cohesion: 0.07
Nodes (27): _base(), upgrade(), ask(), make_context(), history(), AgentRun, AgentStep, Conversation (+19 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.20
Nodes (15): review_contract(), contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model() (+7 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "security.py"
Cohesion: 0.15
Nodes (14): current_user(), _unauthorized(), create_token(), decode_token(), Principal, TokenError, verify_password(), test_alg_none_rejected() (+6 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (89): chunk_pages(), ingest_document(), mark_failed(), extract_pages(), PermanentError, put_pdf(), backfill(), BackfillResult (+81 more)

### Community 17 - "api/documents.py"
Cohesion: 0.12
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 19 - "test_queue.py"
Cohesion: 0.15
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "HttpMetrics"
Cohesion: 0.23
Nodes (5): HttpMetrics, percentile(), test_percentile_interpolates(), test_ring_buffer_is_bounded(), test_summary_groups_by_route_and_counts_5xx_as_errors()

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "client.ts"
Cohesion: 0.21
Nodes (19): ApiError, createConversation(), errorMessage(), getMessages(), json(), listConversations(), listDocuments(), login() (+11 more)

### Community 24 - "api/auth.py"
Cohesion: 0.15
Nodes (12): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+4 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.18
Nodes (28): call(), FakeLLM, say(), Usage, execute(), add_invoice_row(), new_org_user(), corpus() (+20 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.10
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "worker/deps.py"
Cohesion: 0.11
Nodes (7): ToolResult, model_chain_names(), Settings, EmbeddingProvider, call_with_retry(), make_client(), make_s3()

### Community 28 - "tools.py"
Cohesion: 0.15
Nodes (18): AgentContext, _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable() (+10 more)

### Community 29 - "test_eval_harness.py"
Cohesion: 0.15
Nodes (10): FakeReranker, test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), append_docs_row() (+2 more)

### Community 30 - "build_questions.py"
Cohesion: 0.16
Nodes (13): _date(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), _aggregates(), build_questions() (+5 more)

### Community 31 - "test_agent_evals.py"
Cohesion: 0.25
Nodes (9): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+1 more)

### Community 33 - "Evaluation results"
Cohesion: 0.33
Nodes (5): Agent answers, Agent evals (M6), Evaluation results, Load tests (M8), Reproduce

### Community 36 - "test_extraction.py"
Cohesion: 0.26
Nodes (11): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero(), test_money_parsing_tolerates_formats_models_produce() (+3 more)

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
Cohesion: 0.15
Nodes (14): _run(), _run_online(), get_settings(), make_engine(), main(), _main(), main(), _main() (+6 more)

### Community 44 - "tests/conftest.py"
Cohesion: 0.11
Nodes (10): create_app(), client(), configured(), pg(), s3(), sql(), run(), _create_db() (+2 more)

### Community 45 - "logging.py"
Cohesion: 0.15
Nodes (7): clean_request_id(), JsonFormatter, fmt(), test_context_and_extra_fields_are_included(), test_exceptions_are_one_line_json(), test_line_is_json_with_the_standard_fields(), test_request_ids_are_sanitised()

### Community 50 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (32): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+24 more)

### Community 52 - "run_evals.py"
Cohesion: 0.19
Nodes (10): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), evaluate() (+2 more)

### Community 53 - "test_auth.py"
Cohesion: 0.11
Nodes (29): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+21 more)

### Community 54 - "datetime"
Cohesion: 0.15
Nodes (6): ConversationIn, ConversationOut, create(), list_(), MessageOut, get_session()

### Community 55 - "test_search_modes.py"
Cohesion: 0.16
Nodes (13): keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input() (+5 more)

### Community 56 - "contract_extraction.py"
Cohesion: 0.27
Nodes (5): fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields()

### Community 57 - "loop.py"
Cohesion: 0.14
Nodes (8): AgentEvent, snippet(), _step_limit_answer(), validate_citations(), search(), SearchHit, SearchIn, SearchOut

### Community 58 - "LLMResponse"
Cohesion: 0.12
Nodes (7): DemoLLM, GeminiLLM, LLM, LLMResponse, ToolSpec, 0011: Chat streaming and frontend design, CountingLLM

### Community 59 - "auth.tsx"
Cohesion: 0.19
Nodes (18): getMeta(), setUnauthorizedHandler(), tokenStore, App(), AuthContext, AuthProvider(), AuthValue, RequireAuth() (+10 more)

### Community 60 - "test_extract_many.py"
Cohesion: 0.35
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 61 - "reducer.ts"
Cohesion: 0.14
Nodes (16): chatEvents(), KNOWN, parseSSE(), RawSSE, enc, toEvent(), toStreamEvent(), DoneData (+8 more)

### Community 62 - "chunks.py"
Cohesion: 0.17
Nodes (5): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 63 - "lib.sh"
Cohesion: 0.27
Nodes (5): aws_(), die(), need_state(), require_cloudshell_ready(), lib.sh script

### Community 64 - "Deploying Groundwork to AWS (CloudShell runbook)"
Cohesion: 0.20
Nodes (9): 1. Get the code into CloudShell, 2. Create, configure, deploy, 3. Check it works, Day to day, Deploying Groundwork to AWS (CloudShell runbook), Local dry run (no AWS), One-time checks (console), Restore drill (do it once) (+1 more)

### Community 65 - "chat.py"
Cohesion: 0.15
Nodes (7): ConversationNotFound, MessageIn, send(), stream(), sse(), get_limits(), Limits

### Community 66 - "devDependencies"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+12 more)

### Community 67 - "package.json"
Cohesion: 0.08
Nodes (27): dependencies, react, react-dom, react-router-dom, @tanstack/react-query, name, private, type (+19 more)

### Community 72 - "types.ts"
Cohesion: 0.19
Nodes (14): ChatMode, Conversation, DocKind, DocStatus, DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval() (+6 more)

### Community 73 - "DocKind"
Cohesion: 0.22
Nodes (9): Chunk, DocKind, DocStatus, Document, create_with_job(), get_by_sha(), list_for_org(), DocumentOut (+1 more)

### Community 74 - "run_agent"
Cohesion: 0.32
Nodes (6): run_agent(), LLMUnavailable, test_model_outage_ends_the_run_cleanly(), generate(), generate(), generate_stream()

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
Nodes (14): Contract, Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern() (+6 more)

### Community 80 - "Architecture"
Cohesion: 0.40
Nodes (4): Architecture, Deployed (M9): one Docker host, AWS now, Oracle later, Local development, Request path (chat)

### Community 81 - "Observability (M8)"
Cohesion: 0.33
Nodes (5): Cost, GET /admin/metrics, Limits (per API process), Logs, Observability (M8)

### Community 82 - "smoke.py"
Cohesion: 0.15
Nodes (7): call(), main(), multipart(), step(), list_all(), main(), make_pdf()

### Community 84 - "json"
Cohesion: 0.24
Nodes (6): _auth(), main(), _main(), _retry(), _statuses(), _upload()

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.25
Nodes (6): ChatMessage, api, cite, enc, renderChat(), stored

### Community 86 - "health.py"
Cohesion: 0.36
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 91 - "CitedText.test.tsx"
Cohesion: 0.43
Nodes (5): Citation, CitedText(), Props, Segment, splitCitations()

### Community 92 - "extraction.py"
Cohesion: 0.14
Nodes (5): InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), _to_fields()

### Community 94 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 97 - "pytest"
Cohesion: 0.21
Nodes (3): list_models(), main(), probe()

### Community 98 - "ContractFields"
Cohesion: 0.20
Nodes (4): ContractFields, FakeInvoiceExtractor, CountingExtractor, test_fake_extractor_reads_labelled_lines()

### Community 100 - "run_agent_evals.py"
Cohesion: 0.20
Nodes (11): append_agent_rows(), _append_cache(), ask_once(), cache_key(), evaluate_agent(), load_cache(), main(), _main() (+3 more)

### Community 102 - "Hit"
Cohesion: 0.13
Nodes (10): Hit, FlashRankReranker, Reranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 103 - "admin.py"
Cohesion: 0.24
Nodes (3): metrics(), agent_stats(), queue_stats()

### Community 104 - "main.py"
Cohesion: 0.24
Nodes (6): configure_logging(), lifespan(), parse_prices(), build_limits(), main(), test_prices_parse_to_decimal_and_empty_means_none()

### Community 106 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, lint, preview, test, test:watch (+1 more)

### Community 118 - "test_build_retrieval_questions.py"
Cohesion: 0.24
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 119 - "check_extraction.py"
Cohesion: 0.36
Nodes (6): _d(), main(), _main(), _print(), score_contracts(), score_invoices()

### Community 120 - "pathlib"
Cohesion: 0.36
Nodes (3): _explain(), main(), _vec()

## Knowledge Gaps
- **171 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+166 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 599 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **55 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `chat.py`, `run_agent_evals.py`, `sqlalchemy`, `DocKind`, `get_settings`, `run_agent`, `ingestion.py`, `test_search_modes.py`, `loop.py`, `worker/deps.py`, `extraction.py`, `test_eval_harness.py`, `test_agent_loop.py`, `test_agent_evals.py`?**
  _High betweenness centrality (0.044) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `test_observability.py`, `run_agent_evals.py`, `admin.py`, `security.py`, `main.py`, `DocKind`, `Deps`, `tests/conftest.py`, `ingestion.py`, `api/documents.py`, `test_queue.py`, `test_auth.py`, `health.py`, `check_extraction.py`, `api/auth.py`, `worker/deps.py`, `test_eval_harness.py`?**
  _High betweenness centrality (0.027) - this node is a cross-community bridge._
- **Why does `SlidingWindowLimiter` connect `test_observability.py` to `api/auth.py`, `main.py`, `relevant_snippet`?**
  _High betweenness centrality (0.022) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 118 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _171 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_observability.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09882232462877624 - nodes in this community are weakly interconnected._
- **Should `test_gemini_llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11612903225806452 - nodes in this community are weakly interconnected._