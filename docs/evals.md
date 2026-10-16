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
