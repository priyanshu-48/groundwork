# Evaluation results

Retrieval is scored on questions with a known gold **document and page** from the synthetic corpus
(`evals/ground_truth.json`, seed 42):

- **easy** (35 questions, `evals/questions.jsonl`): contract lookups that name the vendor and echo the clause wording.
- **hard** (60 questions, `evals/retrieval_hard.jsonl`): 20 exact invoice-number lookups, 16 invoice
  lookups by vendor + date + total, and 24 paraphrased contract questions that avoid the clause's words.

- **Hit:** a retrieved chunk from the gold document **and** the gold page.
- **Recall@5:** share of questions with a hit in the top 5. **MRR@10:** mean of 1/rank of the first
  hit within the top 10 (0 if none). **Doc recall@5:** same as recall@5 but only the document must match.
- **Search ms:** database + fusion + rerank, with the query already embedded (the Gemini round trip,
  about the same for every mode, is excluded). Rows from before M5 include that round trip.
- Numbers from a fake embedder or fake reranker are never written here; they only check the harness.

| Date | Git SHA | Label | Set | Mode | Embedder | Reranker | Recall@5 | MRR@10 | Doc recall@5 | search p50 ms | search p95 ms |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 | 3aadc7b | baseline (M4) | easy | vector | gemini | - | 100.0% | 0.986 | 100.0% | 470* | 496* |
| 2026-10-17 | 3159355 | m5 | easy | vector | gemini | - | 100.0% | 0.986 | 100.0% | 11 | 24 |
| 2026-10-17 | 3159355 | m5 | easy | hybrid | gemini | - | 97.1% | 0.940 | 100.0% | 18 | 41 |
| 2026-10-17 | 3159355 | m5 | easy | hybrid_rerank | gemini | flashrank:ms-marco-MiniLM-L-12-v2 | 100.0% | 1.000 | 100.0% | 1458 | 1550 |
| 2026-10-17 | 3159355 | m5 | hard | vector | gemini | - | 81.7% | 0.704 | 81.7% | 13 | 65 |
| 2026-10-17 | 3159355 | m5 | hard | hybrid | gemini | - | 93.3% | 0.733 | 96.7% | 36 | 59 |
| 2026-10-17 | 3159355 | m5 | hard | hybrid_rerank | gemini | flashrank:ms-marco-MiniLM-L-12-v2 | 78.3% | 0.714 | 80.0% | 1373 | 1585 |
<!-- evals:end -->

\* includes the ~0.5 s Gemini query-embedding round trip (measured before M5 separated it out).

## Reproduce

From `backend/`, stack up, `GEMINI_API_KEY` set (free tier, synthetic data only):

```bash
uv run python ../evals/generate_corpus.py   # 25 contracts + 300 invoices -> evals/corpus (git-ignored)
uv run python ../evals/build_questions.py   # questions.jsonl (easy, 90) + retrieval_hard.jsonl (60)
uv run python ../evals/load_corpus.py       # upload and wait until every document is ready
uv run python ../evals/run_evals.py --sets easy hard --modes vector hybrid hybrid_rerank --label m5
uv run python ../evals/explain_search.py    # EXPLAIN ANALYZE evidence -> docs/decisions/0006
```

Free-tier limits that shaped the tooling (check AI Studio for your current numbers): embeddings are
capped at about 1000 requests per day, and `generate_content` at about 20 per day. Query vectors are
cached in `evals/.cache/` so reruns do not spend the embedding quota again; the worker can run with
`EXTRACTION_ENABLED=false` to skip invoice extraction.

## Agent evals (M6)

```bash
# from backend/, stack up and corpus loaded
uv run python -m app.worker.backfill_invoices            # extract invoice rows, 10 per LLM call
uv run python ../evals/run_agent_evals.py --types contract_lookup --max-llm-calls 25 --label m6
```

Free-tier notes: finished questions are cached in `evals/.cache/agent_runs.jsonl` (keyed by model
chain, search mode, question and prompt), failed or quota-limited runs are never cached, and a
type's row is written only when all of its questions have an answer. Set `GEMINI_MODELS` to an
ordered list of models and their daily limits from AI Studio (ADR 0009).

**Invoice extraction (live, gemini-3.5-flash-lite, 30 batched calls + 2 retry calls):** 300/300 invoices
extracted and validated; vendor, issue date, due date, currency and total match the ground truth on
every invoice, subtotal on 299/300.

**Reading the agent table:** all 90 questions are answered correctly on this synthetic corpus. Multi-hop
went from 30% to 100% once contract terms became structured data (ADR 0010). Models: the first 10
answers came from gemini-3.5-flash-lite, which then hit its 500/day free quota, and the fallback chain
finished on gemini-3.1-flash-lite (ADR 0009). Known gap: 9 of 35 contract-lookup answers carry no
citation (precision is measured over cited chunks only). Scoring rules and limits: ADR 0008. These
are templated questions over a synthetic corpus, a regression benchmark rather than a claim about
real-world accuracy.

## Agent answers

Real agent (tools + model), answers scored by rules in `evals/scoring.py` (docs/decisions/0008). Citation precision = share of cited chunks that hold the answer, over answers that cite anything (not defined for multi-hop).

| Date | Git SHA | Label | Type | Model(s) | Answered | Accuracy | Citation precision | Avg steps | Avg tokens in/out | p50 s | p95 s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-10-17 | f238874 | m6 | contract_lookup | gemini-3.5-flash-lite | 35/35 | 100.0% | 100.0% | 1.0 | 2912/57 | 9.0 | 9.5 |
| 2026-10-17 | f238874 | m6 | invoice_aggregate | gemini-3.5-flash-lite | 35/35 | 100.0% | 100.0% | 1.0 | 1785/110 | 9.0 | 9.4 |
| 2026-10-17 | f238874 | m6 | multi_hop | gemini-3.5-flash-lite | 20/20 | 30.0% | n/a | 5.0 | 24810/214 | 27.1 | 27.5 |
| 2026-10-17 | 6c45814 | m6c | contract_lookup | gemini-3.1-flash-lite, gemini-3.5-flash-lite | 35/35 | 100.0% | 100.0% | 1.1 | 3445/50 | 9.2 | 26.6 |
| 2026-10-17 | 6c45814 | m6c | invoice_aggregate | gemini-3.1-flash-lite | 35/35 | 100.0% | 100.0% | 1.0 | 2503/115 | 9.1 | 27.7 |
| 2026-10-17 | 6c45814 | m6c | multi_hop | gemini-3.1-flash-lite | 20/20 | 100.0% | n/a | 1.0 | 2509/104 | 8.7 | 22.3 |
<!-- agent:end -->

## Load tests (M8)

Single dev laptop (Windows 11, Docker Desktop), one API process, one worker, Postgres + RustFS in
containers, k6 in a container (`loadtest/`, commands in `loadtest/README.md`). Corpus: 325 documents,
the eval org. Numbers are one run each; treat them as orders of magnitude, not guarantees.

| Test | Setup | Result |
|---|---|---|
| Search, cold | `POST /search`, hybrid, ~1 req/s, 41 unique queries, real Gemini query embeddings | p50 483 ms, p95 538 ms, p99 627 ms, 0 errors |
| Search, warm | same queries from the query-embedding cache, ramp to 20 req/s, 704 requests | p50 15 ms, p95 24 ms, p99 28 ms, 0 errors |
| Chat overhead | 10 concurrent users, own org each, demo model (no Gemini), SSE + search + persistence, 2,921 requests | 72 req/s, p50 122 ms, p95 190 ms, p99 229 ms, 0 errors |
| Per-org limit | 23 requests from one org with `CHAT_RATE_LIMIT_PER_MIN=20` | first 20 `200`, last 3 `429` with `Retry-After` |
| Ingestion | 60 generated PDFs x 3 pages, fake embedder/extractor, 1 worker | 60/60 ready in 3.7 s: ~980 docs/min, ~2,900 pages/min |

**Reading these:** the cold-vs-warm gap (483 ms vs 15 ms) is almost entirely the embedding API round
trip; hybrid search itself is a few ms. A first run mixed cold and warm and showed a misleading warm
p95 of 419 ms, because k6's per-VU iteration counter left half the queries uncached (the script now
uses a scenario-wide counter). The ingestion figure is the pipeline's own ceiling; real ingestion is
limited by the Gemini embedding quota and the min-interval throttle (about 1 request per 2 s on the
free tier), so expect minutes, not seconds, for a real 300-document load. Real chat latency is
dominated by the model (about 9 s per question in M6/M7 runs); our overhead is about 0.1 s.
