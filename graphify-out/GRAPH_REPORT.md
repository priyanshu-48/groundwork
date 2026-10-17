# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 188 files · ~94,582 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 7, .jsonl 2, .example 1)

## Summary
- 1677 nodes · 4828 edges · 98 communities (63 shown, 35 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 334 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91b49fde`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_observability.py
- llm.py
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
- services/metrics.py
- test_model_chain.py
- repositories/conversations.py
- api/auth.py
- test_agent_loop.py
- generate_corpus.py
- logging.py
- tools.py
- check_extraction.py
- 0004_chunks_invoices.py
- test_agent_evals.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- test_extraction.py
- LLMUnavailable
- k6_search.js
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- make_engine
- asyncio
- ingestion.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- Groundwork: Build Spec
- run_evals.py
- test_documents.py
- test_auth.py
- test_search_modes.py
- contract_extraction.py
- loop.py
- Message
- auth.tsx
- test_extract_many.py
- sse.ts
- chunks.py
- search.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- types.ts
- send
- worker/deps.py
- api/conversations.py
- test_gemini_stream.py
- reducer.ts
- compilerOptions
- ContractFields
- probe_models.py
- Observability (M8)
- pathlib
- GeminiInvoiceExtractor
- client.ts
- ChatPage.test.tsx
- storage.py
- PrecomputedEmbedder
- 0013-query-embedding-cache.md
- README.md
- main.py
- ChatPage.tsx
- InvoiceFields
- upload-ask-cite.spec.ts
- dependencies
- run_agent_evals.py

## God Nodes (most connected - your core abstractions)
1. `Deps` - 140 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 43 edges
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

## Communities (98 total, 35 thin omitted)

### Community 0 - "test_observability.py"
Cohesion: 0.07
Nodes (48): ConcurrencyLimiter, SlidingWindowLimiter, chat(), ingest(), _ingest(), new_conv(), parse_sse(), ref_in() (+40 more)

### Community 1 - "llm.py"
Cohesion: 0.12
Nodes (14): clean_schema(), GeminiLLM, LLMError, ModelChain, llm_with(), response(), StubModels, test_every_tool_schema_survives_cleaning_with_its_fields() (+6 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "FakeEmbeddingProvider"
Cohesion: 0.06
Nodes (28): CachedEmbedder, EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), embed() (+20 more)

### Community 4 - "relevant_snippet"
Cohesion: 0.48
Nodes (5): relevant_snippet(), test_falls_back_to_the_opening_when_nothing_matches(), test_is_capped_and_never_empty(), test_picks_the_sentence_that_supports_the_answer_not_the_opening(), test_short_chunks_are_returned_whole()

### Community 5 - "sqlalchemy"
Cohesion: 0.22
Nodes (8): Base, IdMixin, Job, JobStatus, Org, User, create_org_with_user(), get_user_by_email()

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.20
Nodes (15): review_contract(), contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model() (+7 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "security.py"
Cohesion: 0.23
Nodes (11): create_token(), decode_token(), TokenError, verify_password(), test_alg_none_rejected(), test_expired_token_rejected(), test_missing_org_claim_rejected(), test_password_round_trip() (+3 more)

### Community 12 - "Deps"
Cohesion: 0.05
Nodes (100): DocKind, DocStatus, chunk_pages(), ingest_document(), mark_failed(), extract_pages(), PermanentError, hash_password() (+92 more)

### Community 17 - "api/documents.py"
Cohesion: 0.11
Nodes (4): list_documents(), _read_pdf(), upload(), DocumentOut

### Community 19 - "test_queue.py"
Cohesion: 0.11
Nodes (19): create_with_job(), get_by_sha(), list_for_org(), claim(), ClaimedJob, complete(), enqueue(), fail() (+11 more)

### Community 21 - "services/metrics.py"
Cohesion: 0.12
Nodes (10): metrics(), agent_stats(), HttpMetrics, parse_prices(), percentile(), queue_stats(), test_percentile_interpolates(), test_prices_parse_to_decimal_and_empty_means_none() (+2 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "repositories/conversations.py"
Cohesion: 0.30
Nodes (11): AgentRun, AgentStep, Conversation, Message, add_message(), create_conversation(), get_conversation(), history() (+3 more)

### Community 24 - "api/auth.py"
Cohesion: 0.16
Nodes (13): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+5 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.23
Nodes (25): call(), FakeLLM, say(), Usage, execute(), ctx_for(), drain(), last_ref() (+17 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (37): _date(), small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt() (+29 more)

### Community 27 - "logging.py"
Cohesion: 0.11
Nodes (8): clean_request_id(), JsonFormatter, send_with_id(), fmt(), test_context_and_extra_fields_are_included(), test_exceptions_are_one_line_json(), test_line_is_json_with_the_standard_fields(), test_request_ids_are_sanitised()

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (19): AgentContext, _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable() (+11 more)

### Community 29 - "check_extraction.py"
Cohesion: 0.36
Nodes (6): _d(), main(), _main(), _print(), score_contracts(), score_invoices()

### Community 31 - "test_agent_evals.py"
Cohesion: 0.20
Nodes (11): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+3 more)

### Community 33 - "Evaluation results"
Cohesion: 0.33
Nodes (5): Agent answers, Agent evals (M6), Evaluation results, Load tests (M8), Reproduce

### Community 36 - "test_extraction.py"
Cohesion: 0.23
Nodes (12): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero() (+4 more)

### Community 37 - "LLMUnavailable"
Cohesion: 0.11
Nodes (10): call_with_retry(), LLMUnavailable, Throttle, test_model_outage_ends_the_run_cleanly(), generate(), generate(), generate_stream(), test_throttle_spaces_calls_by_the_interval() (+2 more)

### Community 38 - "k6_search.js"
Cohesion: 0.14
Nodes (10): JSON_H, LIMIT, options, VUS, cold(), options, QUERIES, search() (+2 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "make_engine"
Cohesion: 0.14
Nodes (11): _run(), _run_online(), make_engine(), sql(), run(), go(), test_health_degraded_when_s3_missing(), test_health_ok() (+3 more)

### Community 44 - "asyncio"
Cohesion: 0.12
Nodes (9): configured(), pg(), s3(), _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips(), _explain(), main() (+1 more)

### Community 45 - "ingestion.py"
Cohesion: 0.13
Nodes (13): Contract, Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern() (+5 more)

### Community 50 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (32): step(), 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture (+24 more)

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
Cohesion: 0.05
Nodes (35): Hit, keyword_search(), prepare_keyword_query(), specific_terms(), FakeReranker, FlashRankReranker, Reranker, rrf_fuse() (+27 more)

### Community 56 - "contract_extraction.py"
Cohesion: 0.23
Nodes (6): fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields(), _money()

### Community 57 - "loop.py"
Cohesion: 0.12
Nodes (15): LLM, ToolResult, AgentEvent, run_agent(), snippet(), _step_limit_answer(), validate_citations(), ask() (+7 more)

### Community 58 - "Message"
Cohesion: 0.14
Nodes (9): DemoLLM, assemble_stream(), LLMResponse, Message, parse_response(), _to_content(), ToolSpec, test_messages_become_gemini_contents() (+1 more)

### Community 59 - "auth.tsx"
Cohesion: 0.20
Nodes (16): setUnauthorizedHandler(), tokenStore, App(), AuthContext, AuthProvider(), AuthValue, RequireAuth(), app() (+8 more)

### Community 60 - "test_extract_many.py"
Cohesion: 0.35
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 61 - "sse.ts"
Cohesion: 0.29
Nodes (7): chatEvents(), KNOWN, parseSSE(), RawSSE, enc, toEvent(), toStreamEvent()

### Community 62 - "chunks.py"
Cohesion: 0.24
Nodes (8): Chunk, Document, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk, _next_batch()

### Community 65 - "search.py"
Cohesion: 0.36
Nodes (4): search(), SearchHit, SearchIn, SearchOut

### Community 66 - "devDependencies"
Cohesion: 0.07
Nodes (29): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+21 more)

### Community 67 - "package.json"
Cohesion: 0.10
Nodes (21): name, private, type, version, eslint, @eslint/js, eslint-plugin-react-hooks, globals (+13 more)

### Community 72 - "types.ts"
Cohesion: 0.20
Nodes (13): ChatMode, Conversation, DocKind, DocStatus, DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval() (+5 more)

### Community 74 - "worker/deps.py"
Cohesion: 0.11
Nodes (14): get_settings(), model_chain_names(), Settings, FakeInvoiceExtractor, make_client(), make_s3(), main(), _main() (+6 more)

### Community 75 - "api/conversations.py"
Cohesion: 0.12
Nodes (10): ConversationIn, ConversationOut, create(), history(), list_(), MessageOut, current_user(), get_session() (+2 more)

### Community 76 - "test_gemini_stream.py"
Cohesion: 0.25
Nodes (12): ToolCall, chunk(), collect(), llm(), StreamModels, test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model(), test_an_empty_stream_is_an_llm_error(), test_bad_requests_do_not_fall_over_and_exhaustion_is_clear() (+4 more)

### Community 77 - "reducer.ts"
Cohesion: 0.33
Nodes (9): DoneData, StepData, StreamEvent, Action, applyEvent(), idle, reducer(), RunState (+1 more)

### Community 78 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 80 - "probe_models.py"
Cohesion: 0.43
Nodes (3): list_models(), main(), probe()

### Community 81 - "Observability (M8)"
Cohesion: 0.33
Nodes (5): Cost, GET /admin/metrics, Limits (per API process), Logs, Observability (M8)

### Community 82 - "pathlib"
Cohesion: 0.13
Nodes (9): _auth(), main(), _main(), _retry(), _statuses(), _upload(), list_all(), main() (+1 more)

### Community 84 - "client.ts"
Cohesion: 0.32
Nodes (15): ApiError, createConversation(), errorMessage(), getMessages(), getMeta(), json(), listConversations(), listDocuments() (+7 more)

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.22
Nodes (7): ChatMessage, api, cite, enc, renderChat(), stored, @testing-library/user-event

### Community 86 - "storage.py"
Cohesion: 0.23
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 90 - "main.py"
Cohesion: 0.09
Nodes (8): stream(), sse(), configure_logging(), RequestContextMiddleware, create_app(), lifespan(), build_limits(), client()

### Community 91 - "ChatPage.tsx"
Cohesion: 0.23
Nodes (10): Citation, CitationDetail(), CitedText(), Props, Segment, splitCitations(), LABEL, StepsPanel() (+2 more)

### Community 92 - "InvoiceFields"
Cohesion: 0.14
Nodes (3): InvoiceExtractor, InvoiceFields, _LLMInvoice

### Community 94 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, react, react-dom, react-router-dom, @tanstack/react-query

### Community 100 - "run_agent_evals.py"
Cohesion: 0.22
Nodes (10): test_eval_queries_are_never_throttled(), append_agent_rows(), _append_cache(), ask_once(), evaluate_agent(), load_cache(), main(), _main() (+2 more)

## Knowledge Gaps
- **138 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `fixture`, `name` (+133 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 531 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **35 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `step()` connect `Groundwork: Build Spec` to `reducer.ts`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Are the 118 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 118 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _138 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_observability.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0745945945945946 - nodes in this community are weakly interconnected._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.11954022988505747 - nodes in this community are weakly interconnected._
- **Should `FakeEmbeddingProvider` be split into smaller, more focused modules?**
  _Cohesion score 0.06363636363636363 - nodes in this community are weakly interconnected._
- **Should `Deps` be split into smaller, more focused modules?**
  _Cohesion score 0.05002237136465324 - nodes in this community are weakly interconnected._