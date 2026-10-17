# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 119 files · ~66,708 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1082 nodes · 3123 edges · 52 communities (33 shown, 19 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 242 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `787aa0c7`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- sqlalchemy
- worker/deps.py
- run_agent_evals.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- test_eval_harness.py
- test_queue.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- test_model_chain.py
- get_settings
- Hit
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- run_evals.py
- extraction.py
- tests/conftest.py
- ingestion.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- api/documents.py
- upload
- Document
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- test_migrations.py
- health.py
- chunks.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 112 edges
2. `new_org()` - 46 edges
3. `get_settings()` - 34 edges
4. `search_documents()` - 28 edges
5. `process_one()` - 28 edges
6. `seed()` - 28 edges
7. `Hit` - 26 edges
8. `DocKind` - 25 edges
9. `build_deps()` - 25 edges
10. `Message` - 22 edges

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

## Communities (52 total, 19 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.10
Nodes (17): EmbeddingError, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), is_retryable(), _cos(), _provider(), StubModels (+9 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.06
Nodes (32): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus (+24 more)

### Community 6 - "worker/deps.py"
Cohesion: 0.15
Nodes (7): model_chain_names(), Settings, EmbeddingProvider, make_client(), make_s3(), build_deps(), deps()

### Community 7 - "run_agent_evals.py"
Cohesion: 0.08
Nodes (36): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes() (+28 more)

### Community 8 - "api/auth.py"
Cohesion: 0.07
Nodes (36): login(), me(), signup(), _token(), current_user(), _unauthorized(), _EmailIn, LoginIn (+28 more)

### Community 12 - "Deps"
Cohesion: 0.07
Nodes (68): chunk_pages(), ingest_document(), mark_failed(), extract_pages(), PermanentError, backfill(), BackfillResult, Deps (+60 more)

### Community 17 - "test_eval_harness.py"
Cohesion: 0.07
Nodes (28): test_eval_queries_are_never_throttled(), test_every_mode_and_set_reports_all_metrics(), test_fake_embedder_numbers_never_reach_docs_without_opt_in(), test_fake_reranker_numbers_are_refused_too(), test_hard_set_exact_ids_are_found_by_keyword_modes(), test_precomputed_embedder_returns_the_stored_vectors(), test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses() (+20 more)

### Community 19 - "test_queue.py"
Cohesion: 0.20
Nodes (14): claim(), ClaimedJob, complete(), enqueue(), fail(), maker(), _row(), test_duplicate_idempotency_key_is_one_job() (+6 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.15
Nodes (14): DocKind, keyword_search(), search_documents(), RecordingReranker, test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+6 more)

### Community 22 - "test_model_chain.py"
Cohesion: 0.13
Nodes (19): _fall_over_seconds(), retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call(), test_client_errors_never_fall_over() (+11 more)

### Community 23 - "get_settings"
Cohesion: 0.13
Nodes (12): _run(), _run_online(), get_settings(), make_engine(), main(), _main(), run(), go() (+4 more)

### Community 24 - "Hit"
Cohesion: 0.12
Nodes (11): Hit, FakeReranker, FlashRankReranker, Reranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker (+3 more)

### Community 25 - "test_agent_loop.py"
Cohesion: 0.05
Nodes (65): call(), clean_schema(), FakeLLM, GeminiLLM, LLM, LLMError, LLMResponse, Message (+57 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.05
Nodes (28): small(), gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), gt(), qs() (+20 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (16): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+8 more)

### Community 29 - "run_evals.py"
Cohesion: 0.13
Nodes (9): _explain(), main(), _vec(), _auth(), main(), _main(), _retry(), _statuses() (+1 more)

### Community 30 - "extraction.py"
Cohesion: 0.06
Nodes (30): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason() (+22 more)

### Community 31 - "tests/conftest.py"
Cohesion: 0.15
Nodes (6): get_bytes(), client(), configured(), pg(), s3(), sql()

### Community 32 - "ingestion.py"
Cohesion: 0.17
Nodes (3): reap_stale(), run_reaper(), main()

### Community 33 - "Evaluation results"
Cohesion: 0.50
Nodes (3): Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "api/documents.py"
Cohesion: 0.16
Nodes (4): get_session(), create_app(), lifespan(), put_pdf()

### Community 37 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 38 - "Document"
Cohesion: 0.44
Nodes (4): Document, create_with_job(), get_by_sha(), list_for_org()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "test_migrations.py"
Cohesion: 0.38
Nodes (3): _create_db(), _tables(), test_every_migration_applies_from_scratch_and_the_agent_one_round_trips()

### Community 44 - "health.py"
Cohesion: 0.43
Nodes (3): _db_ok(), health(), s3_ok()

### Community 45 - "chunks.py"
Cohesion: 0.20
Nodes (5): fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

## Knowledge Gaps
- **53 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `Rules`, `Git` (+48 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 326 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `ingestion.py`, `sqlalchemy`, `worker/deps.py`, `run_agent_evals.py`, `test_eval_harness.py`, `test_search_modes.py`, `get_settings`, `test_agent_loop.py`, `extraction.py`?**
  _High betweenness centrality (0.102) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `ingestion.py`, `api/documents.py`, `upload`, `worker/deps.py`, `run_agent_evals.py`, `api/auth.py`, `test_migrations.py`, `health.py`, `test_eval_harness.py`, `test_queue.py`, `tests/conftest.py`?**
  _High betweenness centrality (0.046) - this node is a cross-community bridge._
- **Why does `ModelChain` connect `test_agent_loop.py` to `test_model_chain.py`, `extraction.py`, `worker/deps.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Are the 94 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 94 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _53 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `test_embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10084033613445378 - nodes in this community are weakly interconnected._