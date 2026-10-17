# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 169 files · ~87,626 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 15 file(s) not represented in the graph (top: (none) 7, .jsonl 2, .example 1)

## Summary
- 1517 nodes · 4352 edges · 102 communities (60 shown, 42 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 290 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `91b49fde`
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
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- upload
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- pytest
- typing
- is_retryable
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- check_extraction.py
- 0004_chunks_invoices.py
- LLMUnavailable
- Evaluation results
- 0004-synthetic-corpus-design.md
- test_extraction.py
- Throttle
- FakeEmbeddingProvider
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- get_settings
- tests/conftest.py
- Contract
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- Groundwork: Build Spec
- run_agent_evals.py
- test_documents.py
- 8. Milestones (about 3 weeks, one Claude Code session each)
- Hit
- extraction.py
- loop.py
- Message
- auth.tsx
- test_extract_many.py
- sse.ts
- chunks.py
- ingestion.py
- devDependencies
- package.json
- 0010-structured-contract-facts.md
- types.ts
- 6. Key designs (know these well, because they are the interview questions)
- worker/deps.py
- test_gemini_stream.py
- reducer.ts
- compilerOptions
- ContractFields
- backfill_invoices.py
- explain_search.py
- GeminiInvoiceExtractor
- client.ts
- ChatPage.test.tsx
- health.py
- ModelChain
- runner.py
- ChatPage.tsx
- InvoiceFields
- upload-ask-cite.spec.ts
- dependencies

## God Nodes (most connected - your core abstractions)
1. `Deps` - 134 edges
2. `new_org()` - 59 edges
3. `Message` - 40 edges
4. `process_one()` - 38 edges
5. `seed()` - 38 edges
6. `get_settings()` - 38 edges
7. `build_deps()` - 30 edges
8. `make_pdf()` - 30 edges
9. `DocKind` - 29 edges
10. `search_documents()` - 28 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `M8 — Hardening + observability (Day 16)` --references--> `chat()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_chat_api.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py

## Import Cycles
- None detected.

## Communities (102 total, 42 thin omitted)

### Community 0 - "test_chat_api.py"
Cohesion: 0.34
Nodes (19): chat(), ingest(), _ingest(), new_conv(), parse_sse(), ref_in(), set_llm(), signup() (+11 more)

### Community 1 - "llm.py"
Cohesion: 0.14
Nodes (12): assemble_stream(), clean_schema(), LLMError, parse_response(), _to_content(), ToolCall, test_every_tool_schema_survives_cleaning_with_its_fields(), test_messages_become_gemini_contents() (+4 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.27
Nodes (12): EmbeddingError, embed(), _cos(), _provider(), StubModels, test_fake_related_text_scores_higher_than_unrelated(), test_gemini_batches_of_50_and_normalizes(), test_gemini_does_not_retry_client_errors() (+4 more)

### Community 4 - "relevant_snippet"
Cohesion: 0.25
Nodes (8): relevant_snippet(), test_falls_back_to_the_opening_when_nothing_matches(), test_is_capped_and_never_empty(), test_picks_the_sentence_that_supports_the_answer_not_the_opening(), test_short_chunks_are_returned_whole(), Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.21
Nodes (9): Base, IdMixin, Chunk, Job, JobStatus, Org, User, create_org_with_user() (+1 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.20
Nodes (15): review_contract(), contract(), extractor(), good(), Models, test_a_batch_is_one_request_aligned_by_index_and_tolerant_of_formats(), test_a_complete_plausible_contract_is_clean_and_currency_is_uppercased(), test_contract_extraction_falls_over_to_the_next_model() (+7 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.05
Nodes (43): login(), me(), signup(), _token(), MessageIn, send(), stream(), sse() (+35 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (84): chunk_pages(), extract_pages(), PermanentError, backfill(), Deps, process_one(), run_worker(), ingest_corpus() (+76 more)

### Community 17 - "upload"
Cohesion: 0.13
Nodes (4): list_documents(), _read_pdf(), upload(), put_pdf()

### Community 19 - "test_queue.py"
Cohesion: 0.21
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.14
Nodes (14): keyword_search(), search_documents(), corpus(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+6 more)

### Community 22 - "pytest"
Cohesion: 0.13
Nodes (18): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+10 more)

### Community 23 - "typing"
Cohesion: 0.12
Nodes (15): create(), history(), list_(), AgentRun, AgentStep, Conversation, Message, MessageRole (+7 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.19
Nodes (28): call(), FakeLLM, say(), Usage, execute(), add_invoice_row(), new_org_user(), corpus() (+20 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (37): _date(), small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt() (+29 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.11
Nodes (20): AgentContext, _Args, _attr(), contracts_tool(), doc_block(), escape_document_text(), invoices_tool(), _jsonable() (+12 more)

### Community 29 - "check_extraction.py"
Cohesion: 0.36
Nodes (6): _d(), main(), _main(), _print(), score_contracts(), score_invoices()

### Community 31 - "LLMUnavailable"
Cohesion: 0.17
Nodes (10): LLMUnavailable, test_model_outage_ends_the_run_cleanly(), generate(), generate(), generate_stream(), llm_with(), response(), StubModels (+2 more)

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "test_extraction.py"
Cohesion: 0.26
Nodes (11): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero(), test_money_parsing_tolerates_formats_models_produce() (+3 more)

### Community 37 - "Throttle"
Cohesion: 0.27
Nodes (4): Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 38 - "FakeEmbeddingProvider"
Cohesion: 0.18
Nodes (5): FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), test_fake_is_deterministic_768d_and_unit_norm(), M3 — Ingestion worker (Days 5–6)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "get_settings"
Cohesion: 0.11
Nodes (17): _run(), _run_online(), get_settings(), make_engine(), main(), _main(), main(), _main() (+9 more)

### Community 44 - "tests/conftest.py"
Cohesion: 0.13
Nodes (7): client(), configured(), pg(), s3(), _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips()

### Community 45 - "Contract"
Cohesion: 0.19
Nodes (8): Contract, Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern()

### Community 50 - "Groundwork: Build Spec"
Cohesion: 0.15
Nodes (12): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+4 more)

### Community 52 - "run_agent_evals.py"
Cohesion: 0.05
Nodes (37): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+29 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 54 - "8. Milestones (about 3 weeks, one Claude Code session each)"
Cohesion: 0.18
Nodes (11): 8. Milestones (about 3 weeks, one Claude Code session each), M0 — Skeleton (Day 1), M10 — Polish for recruiters (Days 20–21), M1 — Auth + tenancy (Day 2), M2 — Upload, S3, idempotency, job queue (Days 3–4), M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8), M5 — Hybrid search + reranking (Days 9–10), M6 — Agent loop + tools + citations (Days 11–12) (+3 more)

### Community 55 - "Hit"
Cohesion: 0.12
Nodes (11): Hit, FakeReranker, FlashRankReranker, Reranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker (+3 more)

### Community 56 - "extraction.py"
Cohesion: 0.22
Nodes (6): fake_extract(), parse_bool(), parse_int(), parse_percent(), to_fields(), _money()

### Community 57 - "loop.py"
Cohesion: 0.12
Nodes (14): LLM, ToolResult, AgentEvent, run_agent(), snippet(), _step_limit_answer(), validate_citations(), ask() (+6 more)

### Community 58 - "Message"
Cohesion: 0.18
Nodes (6): DemoLLM, GeminiLLM, LLMResponse, Message, ToolSpec, test_generate_disables_auto_function_calling_and_declares_tools()

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
Cohesion: 0.20
Nodes (5): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 65 - "ingestion.py"
Cohesion: 0.17
Nodes (13): DocKind, DocStatus, DocumentOut, ingest_document(), mark_failed(), store_contract(), _store_contract(), store_invoice() (+5 more)

### Community 66 - "devDependencies"
Cohesion: 0.07
Nodes (29): devDependencies, eslint, @eslint/js, eslint-plugin-react-hooks, globals, jsdom, @playwright/test, tailwindcss (+21 more)

### Community 67 - "package.json"
Cohesion: 0.10
Nodes (21): name, private, type, version, eslint, @eslint/js, eslint-plugin-react-hooks, globals (+13 more)

### Community 72 - "types.ts"
Cohesion: 0.20
Nodes (13): ChatMode, Conversation, DocKind, DocStatus, DocumentOut, StatusBadge(), STYLES, documentsRefetchInterval() (+5 more)

### Community 73 - "6. Key designs (know these well, because they are the interview questions)"
Cohesion: 0.22
Nodes (9): step(), 6.1 Idempotent upload, 6.2 Job queue with SKIP LOCKED, 6.3 Ingestion pipeline (worker), 6.4 Hybrid retrieval + reranking, 6.5 Agent loop (hand-written), 6.6 Streaming API, 6.7 Multi-tenancy (+1 more)

### Community 74 - "worker/deps.py"
Cohesion: 0.14
Nodes (7): model_chain_names(), Settings, create_app(), lifespan(), make_client(), make_s3(), deps()

### Community 76 - "test_gemini_stream.py"
Cohesion: 0.27
Nodes (11): chunk(), collect(), llm(), StreamModels, test_a_quota_error_when_the_stream_opens_falls_over_to_the_next_model(), test_an_empty_stream_is_an_llm_error(), test_bad_requests_do_not_fall_over_and_exhaustion_is_clear(), test_function_calls_and_thought_signatures_survive_assembly() (+3 more)

### Community 77 - "reducer.ts"
Cohesion: 0.33
Nodes (9): DoneData, StepData, StreamEvent, Action, applyEvent(), idle, reducer(), RunState (+1 more)

### Community 78 - "compilerOptions"
Cohesion: 0.12
Nodes (15): compilerOptions, isolatedModules, jsx, lib, module, moduleResolution, noEmit, noFallthroughCasesInSwitch (+7 more)

### Community 81 - "backfill_invoices.py"
Cohesion: 0.21
Nodes (6): Document, create_with_job(), get_by_sha(), list_for_org(), BackfillResult, _next_batch()

### Community 82 - "explain_search.py"
Cohesion: 0.10
Nodes (12): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+4 more)

### Community 84 - "client.ts"
Cohesion: 0.32
Nodes (15): ApiError, createConversation(), errorMessage(), getMessages(), getMeta(), json(), listConversations(), listDocuments() (+7 more)

### Community 85 - "ChatPage.test.tsx"
Cohesion: 0.22
Nodes (7): ChatMessage, api, cite, enc, renderChat(), stored, @testing-library/user-event

### Community 86 - "health.py"
Cohesion: 0.36
Nodes (4): _db_ok(), health(), meta(), s3_ok()

### Community 89 - "ModelChain"
Cohesion: 0.18
Nodes (3): call_with_retry(), ModelChain, test_empty_chain_is_rejected()

### Community 91 - "ChatPage.tsx"
Cohesion: 0.23
Nodes (10): Citation, CitationDetail(), CitedText(), Props, Segment, splitCitations(), LABEL, StepsPanel() (+2 more)

### Community 92 - "InvoiceFields"
Cohesion: 0.11
Nodes (5): FakeInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, test_fake_extractor_reads_labelled_lines()

### Community 94 - "dependencies"
Cohesion: 0.40
Nodes (5): dependencies, react, react-dom, react-router-dom, @tanstack/react-query

## Knowledge Gaps
- **124 isolated node(s):** `Rules`, `Git`, `Secrets and AWS cost safety (strict)`, `Free-tier data`, `Hosting portability` (+119 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 478 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **42 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `6. Key designs (know these well, because they are the interview questions)` connect `6. Key designs (know these well, because they are the interview questions)` to `Groundwork: Build Spec`?**
  _High betweenness centrality (0.169) - this node is a cross-community bridge._
- **Why does `step()` connect `6. Key designs (know these well, because they are the interview questions)` to `reducer.ts`?**
  _High betweenness centrality (0.163) - this node is a cross-community bridge._
- **Are the 113 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 113 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `Message` (e.g. with `DemoLLM` and `CannedLLM`) actually correct?**
  _`Message` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Rules`, `Git`, `Secrets and AWS cost safety (strict)` to the rest of the system?**
  _124 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `llm.py` be split into smaller, more focused modules?**
  _Cohesion score 0.14153846153846153 - nodes in this community are weakly interconnected._
- **Should `api/auth.py` be split into smaller, more focused modules?**
  _Cohesion score 0.05070028011204482 - nodes in this community are weakly interconnected._