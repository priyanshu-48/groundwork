# Graph Report - groundwork  (2026-10-17)

## Corpus Check
- 84 files · ~47,476 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 10 file(s) not represented in the graph (top: (none) 5, .example 1, .ini 1)

## Summary
- 640 nodes · 1685 edges · 32 communities (20 shown, 12 thin omitted)
- Extraction: 94% EXTRACTED · 6% INFERRED · 0% AMBIGUOUS · INFERRED: 109 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `fbeda182`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- search_documents
- test_documents.py
- Groundwork: instructions for Claude Code
- test_embeddings.py
- Groundwork journal (interview reference)
- ingestion.py
- extraction.py
- tests/conftest.py
- security.py
- 0001-local-s3-rustfs.md
- Deps
- groundwork
- run_evals.py
- test_queue.py
- 0002-approximate-token-counts.md
- upload
- api/auth.py
- get_settings
- worker/deps.py
- generate_corpus.py
- health.py
- build_questions.py
- test_auth.py
- Evaluation results
- 0004-synthetic-corpus-design.md

## God Nodes (most connected - your core abstractions)
1. `Deps` - 45 edges
2. `get_settings()` - 28 edges
3. `process_one()` - 26 edges
4. `new_org()` - 26 edges
5. `seed()` - 25 edges
6. `build_ground_truth()` - 20 edges
7. `chunk_pages()` - 19 edges
8. `FakeEmbeddingProvider` - 19 edges
9. `make_engine()` - 17 edges
10. `DocKind` - 17 edges

## Surprising Connections (you probably didn't know these)
- `M1 — Auth + tenancy (Day 2)` --references--> `current_user()`  [INFERRED]
  SPEC.md → backend/app/api/deps.py
- `6.1 Idempotent upload` --references--> `ingest()`  [INFERRED]
  SPEC.md → backend/tests/integration/test_retrieval.py
- `0003: Flag doubtful invoices instead of failing or trusting them` --references--> `review_reason()`  [INFERRED]
  docs/decisions/0003-invoice-review-flag.md → backend/app/services/extraction.py
- `6.5 Agent loop (hand-written)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py
- `M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)` --references--> `search_documents()`  [INFERRED]
  SPEC.md → backend/app/services/retrieval.py

## Import Cycles
- None detected.

## Communities (32 total, 12 thin omitted)

### Community 0 - "search_documents"
Cohesion: 0.06
Nodes (32): search_documents(), 10. How to work with Claude Code on this, 11. Metrics to capture (fill these in as you go), 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure), 13. Questions you must be able to answer after building it, 1. What you are building (the 30-second pitch), 2. Tech stack (fixed, so don't let Claude Code swap these), 3. Architecture (+24 more)

### Community 1 - "test_documents.py"
Cohesion: 0.46
Nodes (11): _org(), _pdf(), test_concurrent_identical_uploads_make_one_document(), test_file_lands_in_s3_at_deterministic_key(), test_list_paginates_without_gaps_or_repeats(), test_non_pdf_rejected(), test_orgs_are_isolated(), test_oversized_rejected() (+3 more)

### Community 2 - "Groundwork: instructions for Claude Code"
Cohesion: 0.18
Nodes (10): Commands, Free-tier data, Git, Graphify, graphify, Groundwork: instructions for Claude Code, Hosting portability, Interview journal (+2 more)

### Community 3 - "test_embeddings.py"
Cohesion: 0.08
Nodes (21): EmbeddingError, EmbeddingProvider, FakeEmbeddingProvider, GeminiEmbeddingProvider, _normalize(), call_with_retry(), is_retryable(), Recording (+13 more)

### Community 4 - "Groundwork journal (interview reference)"
Cohesion: 0.50
Nodes (3): Groundwork journal (interview reference), Major decisions, Roadblocks

### Community 5 - "ingestion.py"
Cohesion: 0.06
Nodes (29): Base, IdMixin, Chunk, DocKind, DocStatus, Document, Invoice, Job (+21 more)

### Community 6 - "extraction.py"
Cohesion: 0.08
Nodes (21): _date(), FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor, InvoiceFields, _LLMInvoice, _money(), review_reason() (+13 more)

### Community 7 - "tests/conftest.py"
Cohesion: 0.14
Nodes (6): client(), configured(), pg(), s3(), sql(), run()

### Community 8 - "security.py"
Cohesion: 0.11
Nodes (20): login(), signup(), _token(), _EmailIn, LoginIn, MeOut, SignupIn, TokenOut (+12 more)

### Community 12 - "Deps"
Cohesion: 0.11
Nodes (44): chunk_pages(), Deps, process_one(), run_worker(), invoice_text(), make_due(), make_pdf(), new_org() (+36 more)

### Community 17 - "run_evals.py"
Cohesion: 0.13
Nodes (12): test_empty_input_is_zero_not_a_crash(), test_mrr_at_k_ignores_hits_beyond_k_and_misses(), test_percentile_interpolates(), test_recall_at_k_counts_hits_within_k(), mrr_at_k(), percentile(), recall_at_k(), append_docs_row() (+4 more)

### Community 19 - "test_queue.py"
Cohesion: 0.13
Nodes (16): claim(), ClaimedJob, complete(), enqueue(), fail(), reap_stale(), run_reaper(), maker() (+8 more)

### Community 21 - "upload"
Cohesion: 0.13
Nodes (4): list_documents(), _read_pdf(), upload(), put_pdf()

### Community 22 - "api/auth.py"
Cohesion: 0.14
Nodes (7): me(), current_user(), get_session(), _unauthorized(), create_app(), lifespan(), Principal

### Community 23 - "get_settings"
Cohesion: 0.18
Nodes (10): _run(), _run_online(), get_settings(), make_engine(), go(), deps(), test_health_degraded_when_s3_missing(), test_health_ok() (+2 more)

### Community 25 - "worker/deps.py"
Cohesion: 0.15
Nodes (5): Settings, make_client(), make_s3(), build_deps(), main()

### Community 26 - "generate_corpus.py"
Cohesion: 0.09
Nodes (20): small(), small_corpus(), test_all_files_written_and_pdfs_are_byte_identical_across_runs(), test_every_fact_is_on_its_gold_page(), test_foreign_currency_vendors_only_get_net_15_or_60(), test_full_size_counts(), test_ground_truth_is_deterministic(), test_invoice_math_numbers_and_due_dates() (+12 more)

### Community 27 - "health.py"
Cohesion: 0.43
Nodes (3): _db_ok(), health(), s3_ok()

### Community 30 - "build_questions.py"
Cohesion: 0.08
Nodes (18): gt(), _inv_in_range(), questions(), test_aggregate_answers_match_independent_recomputation(), test_deterministic(), _aggregates(), build_questions(), _in_range() (+10 more)

### Community 31 - "test_auth.py"
Cohesion: 0.41
Nodes (11): _email(), _me(), _signup(), test_duplicate_email_409(), test_invalid_login_is_indistinguishable(), test_login_email_is_case_insensitive(), test_me_rejects_expired_token(), test_me_requires_token() (+3 more)

## Knowledge Gaps
- **41 isolated node(s):** `JobStatus`, `groundwork`, `Rules`, `Git`, `Secrets and AWS cost safety (strict)` (+36 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 214 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **12 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `get_settings()` connect `get_settings` to `ingestion.py`, `tests/conftest.py`, `security.py`, `run_evals.py`, `test_queue.py`, `upload`, `api/auth.py`, `worker/deps.py`, `health.py`, `test_auth.py`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._
- **Why does `8. Milestones (about 3 weeks, one Claude Code session each)` connect `search_documents` to `test_embeddings.py`?**
  _High betweenness centrality (0.054) - this node is a cross-community bridge._
- **Why does `FakeEmbeddingProvider` connect `test_embeddings.py` to `worker/deps.py`, `Deps`, `run_evals.py`, `get_settings`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Are the 34 inferred relationships involving `Deps` (e.g. with `ingest_document()` and `mark_failed()`) actually correct?**
  _`Deps` has 34 INFERRED edges - model-reasoned connections that need verification._
- **What connects `JobStatus`, `groundwork`, `Rules` to the rest of the system?**
  _41 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `search_documents` be split into smaller, more focused modules?**
  _Cohesion score 0.05714285714285714 - nodes in this community are weakly interconnected._
- **Should `test_embeddings.py` be split into smaller, more focused modules?**
  _Cohesion score 0.07505285412262157 - nodes in this community are weakly interconnected._