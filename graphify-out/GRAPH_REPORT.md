# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 121 files · ~69,475 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1100 nodes · 3169 edges · 57 communities (33 shown, 24 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 245 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f238874e`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- Hit
- Groundwork: instructions for Claude Code
- embeddings.py
- Groundwork journal (interview reference)
- typing
- test_auth.py
- test_scoring.py
- api/auth.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- Reranker
- runner.py
- 0002-approximate-token-counts.md
- test_search_modes.py
- ModelChain
- get_settings
- build_ground_truth
- test_agent_loop.py
- generate_corpus.py
- test_rrf.py
- tools.py
- tests/conftest.py
- extraction.py
- Evaluation results
- 0004-synthetic-corpus-design.md
- ingestion.py
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- worker/deps.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- small
- run_agent_evals.py
- test_build_retrieval_questions.py
- build_questions.py
- test_build_questions.py
- chunks.py
- backfill_invoices.py
- pytest

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

## Communities (57 total, 24 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (31): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+23 more)

### Community 1 - "Hit"
Cohesion: 0.12
Nodes (11): Hit, FakeReranker, FlashRankReranker, RecordingReranker, test_real_model_puts_the_relevant_passage_first(), hit(), hit(), StubRanker (+3 more)

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
Cohesion: 0.07
Nodes (30): _base(), upgrade(), AgentRun, AgentStep, Conversation, Message, MessageRole, RunStatus (+22 more)

### Community 6 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.06
Nodes (29): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), list_documents() (+21 more)

### Community 12 - "Deps"
Cohesion: 0.07
Nodes (67): chunk_pages(), extract_pages(), PermanentError, put_pdf(), backfill(), Deps, process_one(), run_worker() (+59 more)

### Community 19 - "runner.py"
Cohesion: 0.11
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.17
Nodes (13): DocKind, keyword_search(), search_documents(), test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing(), test_keyword_survives_odd_input() (+5 more)

### Community 22 - "ModelChain"
Cohesion: 0.08
Nodes (28): _fall_over_seconds(), ModelChain, retry_delay_s(), extractor(), invoice(), Models, test_batches_and_single_extraction_fall_over_to_the_next_model(), test_each_document_is_wrapped_numbered_and_size_capped() (+20 more)

### Community 23 - "get_settings"
Cohesion: 0.16
Nodes (13): _run(), _run_online(), get_settings(), make_engine(), create_app(), lifespan(), run(), go() (+5 more)

### Community 24 - "build_ground_truth"
Cohesion: 0.26
Nodes (8): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth()

### Community 25 - "test_agent_loop.py"
Cohesion: 0.05
Nodes (65): call(), clean_schema(), FakeLLM, GeminiLLM, LLM, LLMError, LLMResponse, Message (+57 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.15
Nodes (11): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+3 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.13
Nodes (16): _Args, _attr(), doc_block(), escape_document_text(), invoices_tool(), _jsonable(), QueryInvoicesArgs, read_tool() (+8 more)

### Community 29 - "tests/conftest.py"
Cohesion: 0.06
Nodes (31): client(), configured(), pg(), s3(), sql(), _org(), _pdf(), test_concurrent_identical_uploads_make_one_document() (+23 more)

### Community 30 - "extraction.py"
Cohesion: 0.12
Nodes (8): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), _to_fields()

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 37 - "ingestion.py"
Cohesion: 0.28
Nodes (6): DocStatus, ingest_document(), mark_failed(), store_invoice(), _store_invoice(), get_bytes()

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 44 - "worker/deps.py"
Cohesion: 0.18
Nodes (6): _db_ok(), health(), model_chain_names(), Settings, make_s3(), s3_ok()

### Community 52 - "run_agent_evals.py"
Cohesion: 0.06
Nodes (40): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried(), test_the_call_budget_stops_early_and_the_next_run_resumes() (+32 more)

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.20
Nodes (3): gt(), qs(), test_counts_ids_and_determinism()

### Community 60 - "build_questions.py"
Cohesion: 0.33
Nodes (7): _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop(), _random_range()

### Community 61 - "test_build_questions.py"
Cohesion: 0.22
Nodes (5): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic()

### Community 62 - "chunks.py"
Cohesion: 0.20
Nodes (6): Chunk, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), TextChunk

### Community 65 - "backfill_invoices.py"
Cohesion: 0.17
Nodes (7): make_client(), BackfillResult, main(), _main(), _next_batch(), build_deps(), main()

### Community 76 - "pytest"
Cohesion: 0.21
Nodes (12): review_reason(), _good(), test_bad_currency_is_flagged(), test_consistent_invoice_is_clean(), test_decimal_arithmetic_has_no_float_drift(), test_fake_extractor_reads_labelled_lines(), test_missing_required_fields_are_flagged(), test_missing_tax_counts_as_zero() (+4 more)

## Knowledge Gaps
- **54 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `Rules`, `Git` (+49 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 332 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `backfill_invoices.py`, `embeddings.py`, `ingestion.py`, `worker/deps.py`, `runner.py`, `run_agent_evals.py`, `test_search_modes.py`, `get_settings`, `test_agent_loop.py`, `extraction.py`?**
  _High betweenness centrality (0.084) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `backfill_invoices.py`, `test_auth.py`, `api/auth.py`, `worker/deps.py`, `runner.py`, `run_agent_evals.py`, `tests/conftest.py`?**
  _High betweenness centrality (0.048) - this node is a cross-community bridge._
- **Why does `ModelChain` connect `ModelChain` to `backfill_invoices.py`, `test_agent_loop.py`, `worker/deps.py`, `extraction.py`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **Are the 96 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 96 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _54 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.0625 - nodes in this community are weakly interconnected._
- **Should `Hit` be split into smaller, more focused modules?**
  _Cohesion score 0.1164021164021164 - nodes in this community are weakly interconnected._