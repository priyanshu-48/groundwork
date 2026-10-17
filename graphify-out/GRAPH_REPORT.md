# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 132 files · ~76,083 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 11 file(s) not represented in the graph (top: (none) 5, .jsonl 2, .example 1)

## Summary
- 1218 nodes · 3627 edges · 72 communities (41 shown, 31 thin omitted)
- Extraction: 92% EXTRACTED · 8% INFERRED · 0% AMBIGUOUS · INFERRED: 282 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `6c458144`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Groundwork: Build Spec
- Hit
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
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
- ModelChain
- conversations.py
- worker/deps.py
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
- FakeEmbeddingProvider
- 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
- 0005_tsv_split_hyphens.py
- 0005-keyword-search-design.md
- integration/conftest.py
- tests/conftest.py
- invoices.py
- 0007-query-invoices-extensions.md
- 0008-answer-scoring.md
- 0009-model-fallback.md
- get_settings
- run_agent_evals.py
- test_documents.py
- retrieval.py
- test_rerank.py
- api/documents.py
- search_tool
- test_build_retrieval_questions.py
- build_ground_truth
- build_questions.py
- test_build_questions.py
- chunks.py
- ingestion.py
- small
- UnrelatedQueryEmbedder
- 0010-structured-contract-facts.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 135 edges
2. `new_org()` - 59 edges
3. `get_settings()` - 38 edges
4. `process_one()` - 35 edges
5. `seed()` - 35 edges
6. `DocKind` - 29 edges
7. `search_documents()` - 28 edges
8. `build_deps()` - 28 edges
9. `make_pdf()` - 27 edges
10. `AgentContext` - 26 edges

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

## Communities (72 total, 31 thin omitted)

### Community 0 - "Groundwork: Build Spec"
Cohesion: 0.06
Nodes (30): 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture, 4. Repository layout (+22 more)

### Community 1 - "Hit"
Cohesion: 0.16
Nodes (5): Hit, FlashRankReranker, RecordingReranker, test_real_model_puts_the_relevant_passage_first(), hit()

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.18
Nodes (14): EmbeddingError, is_retryable(), embed(), _cos(), _provider(), StubModels, test_daily_quota_429_is_not_retried_but_per_minute_429_is(), test_fake_related_text_scores_higher_than_unrelated() (+6 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "sqlalchemy"
Cohesion: 0.22
Nodes (10): AgentRun, AgentStep, Base, IdMixin, Job, JobStatus, Org, User (+2 more)

### Community 6 - "test_contract_extraction.py"
Cohesion: 0.11
Nodes (22): ContractFields, fake_extract(), parse_bool(), parse_int(), parse_percent(), review_contract(), to_fields(), CountingExtractor (+14 more)

### Community 7 - "test_scoring.py"
Cohesion: 0.16
Nodes (17): q(), test_citation_precision_for_aggregates_uses_vendor_and_date_range(), test_citation_precision_for_contract_lookups_needs_document_and_page(), test_contract_answers(), test_count_is_not_fooled_by_dates_or_invoice_numbers(), test_list_needs_exactly_the_right_invoices(), test_multi_hop_total_is_a_decimal_match(), test_multi_hop_vendor_must_be_named_alone() (+9 more)

### Community 8 - "api/auth.py"
Cohesion: 0.07
Nodes (37): login(), me(), signup(), _token(), current_user(), get_session(), _unauthorized(), _EmailIn (+29 more)

### Community 12 - "Deps"
Cohesion: 0.05
Nodes (88): chunk_pages(), TextChunk, ingest_document(), mark_failed(), extract_pages(), PermanentError, put_pdf(), backfill() (+80 more)

### Community 17 - "upload"
Cohesion: 0.15
Nodes (3): list_documents(), _read_pdf(), upload()

### Community 19 - "test_queue.py"
Cohesion: 0.14
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "test_search_modes.py"
Cohesion: 0.18
Nodes (13): DocKind, keyword_search(), search_documents(), corpus(), test_every_mode_respects_org_isolation_and_kind(), test_hybrid_recovers_a_keyword_hit_the_vector_side_misses(), test_keyword_finds_an_invoice_by_its_exact_number(), test_keyword_stop_words_only_returns_nothing() (+5 more)

### Community 22 - "ModelChain"
Cohesion: 0.10
Nodes (20): _fall_over_seconds(), ModelChain, retry_delay_s(), api_error(), Clock, make(), test_all_models_exhausted_is_a_clear_error(), call() (+12 more)

### Community 23 - "conversations.py"
Cohesion: 0.33
Nodes (9): Conversation, Message, MessageRole, RunStatus, add_message(), create_conversation(), get_conversation(), history() (+1 more)

### Community 24 - "worker/deps.py"
Cohesion: 0.17
Nodes (5): model_chain_names(), Settings, call_with_retry(), make_client(), BackfillResult

### Community 25 - "test_agent_loop.py"
Cohesion: 0.06
Nodes (64): call(), clean_schema(), FakeLLM, GeminiLLM, LLM, LLMError, LLMResponse, Message (+56 more)

### Community 26 - "generate_corpus.py"
Cohesion: 0.15
Nodes (11): _doc(), _facts(), main(), _money(), _norm(), _q(), _render_contract(), render_corpus() (+3 more)

### Community 27 - "test_rrf.py"
Cohesion: 0.20
Nodes (11): prepare_keyword_query(), specific_terms(), rrf_fuse(), test_agreement_beats_a_single_high_rank(), test_empty_inputs(), test_k_controls_how_much_top_ranks_dominate(), test_prepare_keyword_query_turns_identifiers_into_phrases(), test_raw_scores_never_matter_only_ranks() (+3 more)

### Community 28 - "tools.py"
Cohesion: 0.17
Nodes (13): _Args, contracts_tool(), invoices_tool(), _jsonable(), QueryContractsArgs, QueryInvoicesArgs, read_tool(), ReadArgs (+5 more)

### Community 29 - "pathlib"
Cohesion: 0.08
Nodes (18): _d(), main(), _main(), _print(), score_contracts(), score_invoices(), _explain(), main() (+10 more)

### Community 33 - "Evaluation results"
Cohesion: 0.40
Nodes (4): Agent answers, Agent evals (M6), Evaluation results, Reproduce

### Community 36 - "InvoiceFields"
Cohesion: 0.06
Nodes (29): FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason(), _to_fields() (+21 more)

### Community 37 - "Throttle"
Cohesion: 0.17
Nodes (5): GeminiEmbeddingProvider, Throttle, test_throttle_spaces_calls_by_the_interval(), fake_sleep(), test_zero_interval_never_sleeps()

### Community 38 - "FakeEmbeddingProvider"
Cohesion: 0.20
Nodes (5): EmbeddingProvider, FakeEmbeddingProvider, _normalize(), test_fake_is_deterministic_768d_and_unit_norm(), M3 — Ingestion worker (Days 5–6)

### Community 39 - "0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)"
Cohesion: 0.25
Nodes (7): 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand), Keyword query (OR tsquery, GIN on tsv), Keyword query with sequential scans disabled, Vector query, iterative_scan = off, Vector query, iterative_scan = relaxed_order, Vector query with sequential scans disabled (proves the HNSW index is usable), What this shows

### Community 40 - "0005_tsv_split_hyphens.py"
Cohesion: 0.83
Nodes (3): downgrade(), _rebuild(), upgrade()

### Community 42 - "integration/conftest.py"
Cohesion: 0.17
Nodes (7): _run(), _run_online(), make_engine(), create_app(), lifespan(), make_s3(), deps()

### Community 44 - "tests/conftest.py"
Cohesion: 0.08
Nodes (14): _db_ok(), health(), get_bytes(), s3_ok(), client(), configured(), pg(), s3() (+6 more)

### Community 45 - "invoices.py"
Cohesion: 0.19
Nodes (7): Invoice, delete_for_document(), query(), aggregate(), delete_for_document(), find_trusted(), like_pattern()

### Community 50 - "get_settings"
Cohesion: 0.18
Nodes (11): get_settings(), main(), _main(), main(), _main(), build_deps(), main(), test_health_degraded_when_s3_missing() (+3 more)

### Community 52 - "run_agent_evals.py"
Cohesion: 0.05
Nodes (41): CannedLLM, run(), test_a_rerun_uses_the_cache_and_makes_no_llm_calls(), test_accuracy_counts_right_and_wrong_answers(), test_cache_keys_change_with_the_model_chain_and_search_mode(), test_cache_misses_when_a_tool_definition_changes(), test_docs_rows_only_for_complete_types_and_never_for_fakes(), test_failed_runs_are_not_cached_and_are_retried() (+33 more)

### Community 53 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 55 - "test_rerank.py"
Cohesion: 0.24
Nodes (6): FakeReranker, hit(), StubRanker, test_empty_candidates_skip_the_model(), test_fake_reranker_orders_by_word_overlap_and_caps_top_k(), test_flashrank_adapter_maps_ids_sorts_by_score_and_stays_off_the_loop()

### Community 57 - "search_tool"
Cohesion: 0.40
Nodes (4): _attr(), doc_block(), escape_document_text(), search_tool()

### Community 58 - "test_build_retrieval_questions.py"
Cohesion: 0.22
Nodes (3): gt(), qs(), test_counts_ids_and_determinism()

### Community 59 - "build_ground_truth"
Cohesion: 0.26
Nodes (8): small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates(), build_ground_truth()

### Community 60 - "build_questions.py"
Cohesion: 0.25
Nodes (9): _date(), test_deterministic(), _aggregates(), build_questions(), _in_range(), _lookups(), main(), _multi_hop() (+1 more)

### Community 61 - "test_build_questions.py"
Cohesion: 0.28
Nodes (4): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation()

### Community 62 - "chunks.py"
Cohesion: 0.18
Nodes (10): Chunk, Document, fetch_by_ids(), first_chunks(), replace_for_document(), vector_search(), create_with_job(), get_by_sha() (+2 more)

### Community 65 - "ingestion.py"
Cohesion: 0.26
Nodes (6): Contract, store_contract(), _store_contract(), backfill(), BackfillResult, _next_batch()

## Knowledge Gaps
- **55 isolated node(s):** `Tool`, `JobStatus`, `groundwork`, `Rules`, `Git` (+50 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 362 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **31 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Deps` connect `Deps` to `ingestion.py`, `InvoiceFields`, `FakeEmbeddingProvider`, `integration/conftest.py`, `get_settings`, `run_agent_evals.py`, `test_search_modes.py`, `worker/deps.py`, `test_agent_loop.py`, `chunks.py`?**
  _High betweenness centrality (0.116) - this node is a cross-community bridge._
- **Why does `search_documents()` connect `test_search_modes.py` to `Groundwork: Build Spec`, `Hit`, `FakeEmbeddingProvider`, `Deps`, `run_agent_evals.py`, `retrieval.py`, `search_tool`, `test_rrf.py`, `tools.py`, `chunks.py`?**
  _High betweenness centrality (0.036) - this node is a cross-community bridge._
- **Why does `get_settings()` connect `get_settings` to `ingestion.py`, `api/auth.py`, `integration/conftest.py`, `tests/conftest.py`, `Deps`, `upload`, `test_queue.py`, `run_agent_evals.py`, `api/documents.py`, `worker/deps.py`, `pathlib`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **Are the 115 inferred relationships involving `Deps` (e.g. with `ask()` and `make_context()`) actually correct?**
  _`Deps` has 115 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Tool`, `JobStatus`, `groundwork` to the rest of the system?**
  _55 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Groundwork: Build Spec` be split into smaller, more focused modules?**
  _Cohesion score 0.06451612903225806 - nodes in this community are weakly interconnected._
- **Should `test_contract_extraction.py` be split into smaller, more focused modules?**
  _Cohesion score 0.10569105691056911 - nodes in this community are weakly interconnected._