# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 120 files · ~67,865 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1095 nodes · 3167 edges · 60 communities (38 shown, 22 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 245 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fa71354f`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- embeddings.py
- Groundwork journal (interview reference)
- typing
- asyncio
- test_scoring.py
- security.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- api/auth.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- ModelChain
- get_settings
- Hit
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- explain_search.py
- ingestion.py
- tests/conftest.py
- backfill_invoices.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- api/documents.py
- upload
- build_ground_truth
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- test_auth.py
- storage.py
- Chunk
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- run_agent_evals.py
- small
- current_user
- test_build_retrieval_questions.py
- build_questions.py
- test_build_questions.py
- chunks.py
- worker/deps.py

## God Nodes (most connected - your core abstractions)
1. `Deps` - 114 edges
2. `new_org()` - 48 edges
3. `get_settings()` - 34 edges
4. `search_documents()` - 28 edges
5. `process_one()` - 28 edges
6. `seed()` - 28 edges
7. `Hit` - 26 edges
8. `DocKind` - 25 edges
9. `build_deps()` - 25 edges
10. `AgentContext` - 23 edges

## Surprising Connections (you probably didn't know these)
- `M6 — Agent loop + tools + citations (Days 11–12)` --references--> `FakeLLM`  [INFERRED]
  SPEC.md → backend/app/agent/llm.py
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py

## Import Cycles
- None detected.

## Communities (60 total, 22 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "embeddings.py"
Cohesion: 0.07
Nodes (24): EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), Throttle, embed() (+16 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "typing"
Cohesion: 0.08
Nodes (25): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus (+17 more)

### Community 6 - "asyncio"
Cohesion: 0.24
Nodes (3): reap_stale(), run_reaper(), main()

### Community 7 - "test_scoring.py"
Cohesion: 0.17
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "security.py"
Cohesion: 0.20
Nodes (12): create_token(), decode_token(), hash_password(), TokenError, verify_password(), test_alg_none_rejected(), test_expired_token_rejected(), test_missing_org_claim_rejected() (+4 more)

### Community 12 - "Deps"
Cohesion: 0.06
Nodes (69): chunk_pages(), ingest_document(), mark_failed(), extract_pages(), PermanentError, put_pdf(), backfill(), Deps (+61 more)

### Community 17 - "api/auth.py"
Cohesion: 0.24
Nodes (9): login(), me(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn (+1 more)

### Community 19 - "test_queue.py"
Cohesion: 0.21
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.16
Nodes (14): DocKind, keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+6 more)

### Community 22 - "ModelChain"
Cohesion: 0.10
Nodes (20): _fall_over_seconds(), ModelChain, retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call() (+12 more)

### Community 23 - "get_settings"
Cohesion: 0.16
Nodes (7): _run(), _run_online(), get_settings(), test_health_degraded_when_s3_missing(), test_health_ok(), test_migration_enabled_pgvector(), q()

### Community 24 - "Hit"
Cohesion: 0.13
Nodes (10): Hit, FakeReranker, FlashRankReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker, test_empty_candidates_skip_the_model() (+2 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.06
Nodes (64): call(), clean_schema(), FakeLLM, GeminiLLM, LLM, LLMError, LLMResponse, Message (+56 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.16
Nodes (10): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+2 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (16): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+8 more)

### Community 29 - "explain_search.py"
Cohesion: 0.11
Nodes (12): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+4 more)

### Community 30 - "ingestion.py"
Cohesion: 0.05
Nodes (36): Invoice, aggregate(), delete_for_document(), find_trusted(), _like(), _date(), GeminiInvoiceExtractor, InvoiceExtractor (+28 more)

### Community 31 - "tests/conftest.py"
Cohesion: 0.13
Nodes (10): client(), configured(), pg(), s3(), sql(), run(), go(), _create_db() (+2 more)

### Community 32 - "backfill_invoices.py"
Cohesion: 0.24
Nodes (4): BackfillResult, main(), _main(), _next_batch()

### Community 33 - "Evaluation results"
Cohesion: 0.50
Nodes (3): Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "api/documents.py"
Cohesion: 0.20
Nodes (3): get_session(), DocStatus, DocumentOut

### Community 37 - "upload"
Cohesion: 0.14
Nodes (4): list_documents(), _read_pdf(), upload(), Principal

### Community 38 - "build_ground_truth"
Cohesion: 0.23
Nodes (9): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth() (+1 more)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 44 - "storage.py"
Cohesion: 0.18
Nodes (5): _db_ok(), health(), create_app(), lifespan(), s3_ok()

### Community 45 - "Chunk"
Cohesion: 0.29
Nodes (5): Chunk, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search()

### Community 52 - "run_agent_evals.py"
Cohesion: 0.06
Nodes (39): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes() (+31 more)

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.19
Nodes (4): gt(), qs(), test_counts_ids_and_determinism(), build_retrieval_questions()

### Community 60 - "build_questions.py"
Cohesion: 0.33
Nodes (7): _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "test_build_questions.py"
Cohesion: 0.22
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 65 - "worker/deps.py"
Cohesion: 0.20
Nodes (8): model_chain_names(), Settings, make_engine(), FakeInvoiceExtractor, make_client(), make_s3(), build_deps(), deps()

## Knowledge Gaps
- **53 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `Rules`, `Git` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 327 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **22 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `backfill_invoices.py`, `worker/deps.py`, `embeddings.py`, `run_agent_evals.py`, `test_search_modes.py`, `test_agent_loop.py`, `ingestion.py`?**
  _High betweenness centrality (0.091) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `backfill_invoices.py`, `worker/deps.py`, `api/documents.py`, `upload`, `asyncio`, `security.py`, `test_auth.py`, `storage.py`, `Deps`, `api/auth.py`, `test_queue.py`, `run_agent_evals.py`, `current_user`, `tests/conftest.py`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `ModelChain` connect `ModelChain` to `worker/deps.py`, `test_agent_loop.py`, `embeddings.py`, `ingestion.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 96 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 96 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.0660377358490566 - nodes in this community are weakly interconnected._