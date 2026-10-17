# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 169 files · ~87,626 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 7, .jsonl 2, .example 1)

## Summary
- 1496 nodes · 4364 edges · 96 communities (62 shown, 34 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 314 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4118788f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- test_chat_api.py
- llm.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- relevant_snippet
- sqlalchemy
- test_contract_extraction.py
- test_scoring.py
- security.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- upload
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- repositories/conversations.py
- typing
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- pathlib
- 0004_chunks_invoices.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- InvoiceFields
- Throttle
- worker/deps.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- get_settings
- tests/conftest.py
- ingestion.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- test_auth.py
- run_agent_evals.py
- test_documents.py
- retrieval.py
- Hit
- datetime
- loop.py
- Message
- auth.tsx
- test_extract_many.py
- ChatPage.tsx
- chunks.py
- backfill_contracts.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- DocumentsPage.tsx
- api/auth.py
- chat.py
- api/conversations.py
- test_gemini_stream.py
- types.ts
- compilerOptions
- api/documents.py
- DocKind
- backfill_invoices.py
- load_corpus.py
- GeminiInvoiceExtractor
- client.ts
- ChatPage.test.tsx
- health.py
- scripts
- argparse
- ModelChain
- reaper.py
- CitedText.test.tsx
- InvoiceExtractor
- upload-ask-cite.spec.ts
- dependencies
- vite.config.ts

## God Nodes (most connected - your core abstractions)
1. `Deps` - 137 edges
2. `new_org()` - 59 edges
3. `Message` - 38 edges
4. `get_settings()` - 38 edges
5. `process_one()` - 38 edges
6. `seed()` - 38 edges
7. `build_deps()` - 32 edges
8. `make_pdf()` - 30 edges
9. `DocKind` - 29 edges
10. `search_documents()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `0011: Chat streaming and frontend design` --references--> `DemoLLM`  [INFERRED]
  docs/decisions/0011-chat-streaming-and-frontend.md → backend/app/agent/demo.py

## Import Cycles
- None detected.

## Communities (96 total, 34 thin omitted)

### Community 0 - "test_chat_api.py"
Cohesion: 0.07
Nodes (53): chat(), ingest(), _ingest(), new_conv(), parse_sse(), ref_in(), set_llm(), signup() (+45 more)

### Community 1 - "llm.py"
Cohesion: 0.13
Nodes (16): assemble_stream(), clean_schema(), GeminiLLM, LLMError, parse_response(), ToolCall, llm_with(), response() (+8 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.22
Nodes (12): EmbeddingError, embed(), _cos(), _provider(), StubModels, test_fake_related_text_scores_higher_than_unrelated(), test_gemini_batches_of_50_and_normalizes(), test_gemini_does_not_retry_client_errors() (+4 more)

### Community 4 - "relevant_snippet"
Cohesion: 0.25
Nodes (8): relevant_snippet(), test_falls_back_to_the_opening_when_nothing_matches(), test_is_capped_and_never_empty(), test_picks_the_sentence_that_supports_the_answer_not_the_opening(), test_short_chunks_are_returned_whole(), Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.23
Nodes (8): Base, IdMixin, Job, JobStatus, Org, User, create_org_with_user(), get_user_by_email()

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.09
Nodes (25): ContractFields, fake_extract(), parse_bool(), parse_int(), parse_percent(), review_contract(), to_fields(), _money() (+17 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "security.py"
Cohesion: 0.22
Nodes (12): create_token(), decode_token(), hash_password(), TokenError, verify_password(), test_alg_none_rejected(), test_expired_token_rejected(), test_missing_org_claim_rejected() (+4 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (89): DocStatus, chunk_pages(), TextChunk, ingest_document(), mark_failed(), extract_pages(), PermanentError, put_pdf() (+81 more)

### Community 17 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 19 - "test_queue.py"
Cohesion: 0.21
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.18
Nodes (12): keyword_search(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input(), test_keyword_uses_or_semantics_so_one_unmatched_word_does_not_zero_the_result() (+4 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.16
Nodes (18): retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over(), call() (+10 more)

### Community 23 - "repositories/conversations.py"
Cohesion: 0.27
Nodes (13): AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus, add_message(), create_conversation() (+5 more)

### Community 24 - "typing"
Cohesion: 0.22
Nodes (4): call_with_retry(), _fall_over_seconds(), is_retryable(), test_daily_quota_429_is_not_retried_but_per_minute_429_is()

### Community 25 - "test_agent_loop.py"
Cohesion: 0.23
Nodes (25): call(), FakeLLM, say(), Usage, execute(), new_org_user(), ctx_for(), drain() (+17 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (37): _date(), small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt() (+29 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (19): AgentContext, _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable() (+11 more)

### Community 29 - "pathlib"
Cohesion: 0.18
Nodes (9): _d(), main(), _main(), _print(), score_contracts(), score_invoices(), _explain(), main() (+1 more)

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "InvoiceFields"
Cohesion: 0.16
Nodes (12): FakeInvoiceExtractor, InvoiceFields, review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines() (+4 more)

### Community 37 - "Throttle"
Cohesion: 0.21
Nodes (4): Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 38 - "worker/deps.py"
Cohesion: 0.11
Nodes (11): model_chain_names(), Settings, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), make_client(), make_s3() (+3 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "get_settings"
Cohesion: 0.13
Nodes (13): _run(), _run_online(), get_settings(), make_engine(), main(), _main(), run(), go() (+5 more)

### Community 44 - "tests/conftest.py"
Cohesion: 0.10
Nodes (11): create_app(), lifespan(), get_bytes(), client(), configured(), pg(), s3(), sql() (+3 more)

### Community 45 - "ingestion.py"
Cohesion: 0.14
Nodes (12): Contract, Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern() (+4 more)

### Community 50 - "test_auth.py"
Cohesion: 0.36
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 52 - "run_agent_evals.py"
Cohesion: 0.05
Nodes (37): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+29 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 55 - "Hit"
Cohesion: 0.13
Nodes (10): Hit, FakeReranker, FlashRankReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 57 - "loop.py"
Cohesion: 0.13
Nodes (15): LLM, ToolResult, AgentEvent, run_agent(), snippet(), _step_limit_answer(), validate_citations(), ask() (+7 more)

### Community 58 - "Message"
Cohesion: 0.16
Nodes (8): DemoLLM, LLMResponse, Message, _to_content(), ToolSpec, test_messages_become_gemini_contents(), test_raw_model_content_is_replayed_verbatim(), CountingLLM

### Community 59 - "auth.tsx"
Cohesion: 0.22
Nodes (15): setUnauthorizedHandler(), tokenStore, App(), AuthContext, AuthProvider(), AuthValue, RequireAuth(), app() (+7 more)

### Community 60 - "test_extract_many.py"
Cohesion: 0.31
Nodes (8): extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped(), test_empty_batch_makes_no_call(), test_missing_or_garbled_entries_become_flagged_empties(), test_one_request_serves_the_whole_batch_and_results_line_up_by_index()

### Community 61 - "ChatPage.tsx"
Cohesion: 0.18
Nodes (16): createConversation(), getMessages(), sendMessage(), chatEvents(), KNOWN, parseSSE(), RawSSE, enc (+8 more)

### Community 62 - "chunks.py"
Cohesion: 0.26
Nodes (5): Chunk, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search()

### Community 65 - "backfill_contracts.py"
Cohesion: 0.36
Nodes (5): backfill(), BackfillResult, main(), _main(), _next_batch()

### Community 66 - "devDependencies"
Cohesion: 0.10
Nodes (20): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+12 more)

### Community 67 - "package.json"
Cohesion: 0.12
Nodes (17): name, private, type, version, eslint, @eslint/js, eslint-plugin-react-hooks, globals (+9 more)

### Community 72 - "DocumentsPage.tsx"
Cohesion: 0.19
Nodes (12): DocKind, DocStatus, DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval(), MAX_UPLOAD_BYTES, validateUpload() (+4 more)

### Community 73 - "api/auth.py"
Cohesion: 0.24
Nodes (9): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+1 more)

### Community 74 - "chat.py"
Cohesion: 0.14
Nodes (4): MessageIn, send(), stream(), sse()

### Community 75 - "api/conversations.py"
Cohesion: 0.20
Nodes (7): ConversationIn, ConversationOut, create(), history(), list_(), MessageOut, Principal

### Community 76 - "test_gemini_stream.py"
Cohesion: 0.27
Nodes (11): chunk(), collect(), llm(), StreamModels, test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model(), test_an_empty_stream_is_an_llm_error(), test_bad_requests_do_not_fall_over_and_exhaustion_is_clear(), test_function_calls_and_thought_signatures_survive_assembly() (+3 more)

### Community 77 - "types.ts"
Cohesion: 0.23
Nodes (12): ChatMode, Conversation, DoneData, StepData, StreamEvent, Action, applyEvent(), idle (+4 more)

### Community 78 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 79 - "api/documents.py"
Cohesion: 0.17
Nodes (3): current_user(), get_session(), _unauthorized()

### Community 80 - "DocKind"
Cohesion: 0.22
Nodes (7): DocKind, search_documents(), Recording, test_another_org_sees_nothing(), test_query_is_embedded_with_the_query_task(), test_questions_find_their_contract_and_mostly_their_page(), test_results_are_ranked_capped_and_filterable()

### Community 81 - "backfill_invoices.py"
Cohesion: 0.23
Nodes (6): Document, create_with_job(), get_by_sha(), list_for_org(), BackfillResult, _next_batch()

### Community 82 - "load_corpus.py"
Cohesion: 0.24
Nodes (6): _auth(), main(), _main(), _retry(), _statuses(), _upload()

### Community 83 - "GeminiInvoiceExtractor"
Cohesion: 0.23
Nodes (3): GeminiInvoiceExtractor, _LLMInvoice, _to_fields()

### Community 84 - "client.ts"
Cohesion: 0.39
Nodes (10): ApiError, errorMessage(), getMeta(), json(), listConversations(), listDocuments(), login(), request() (+2 more)

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.18
Nodes (9): ChatMessage, api, cite, enc, renderChat(), stored, @testing-library/jest-dom, @testing-library/react (+1 more)

### Community 86 - "health.py"
Cohesion: 0.36
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 87 - "scripts"
Cohesion: 0.22
Nodes (9): scripts, build, dev, e2e, lint, preview, test, test:watch (+1 more)

### Community 88 - "argparse"
Cohesion: 0.36
Nodes (3): list_models(), main(), probe()

### Community 91 - "CitedText.test.tsx"
Cohesion: 0.43
Nodes (5): Citation, CitedText(), Props, Segment, splitCitations()

### Community 94 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, react, react-dom, react-router-dom, @tanstack/react-query

## Knowledge Gaps
- **124 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `fixture`, `name` (+119 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 458 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **34 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `step()` connect `test_chat_api.py` to `types.ts`?**
  _High betweenness centrality (0.202) - this node is a cross-community bridge._
- **Are the 116 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 116 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Message` (e.g. with `DemoLLM` and `CannedLLM`) actually correct?**
  _`Message` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _124 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `test_chat_api.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07205513784461152 - nodes in this community are weakly interconnected._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.1310344827586207 - nodes in this community are weakly interconnected._
- **Should `test_contract_extraction.py` be split into smaller, more focused modules?**
  _Cohesion score 0.08953900709219859 - nodes in this community are weakly interconnected._