# Evaluation results

Retrieval is scored on the 35 contract-lookup questions of the synthetic eval set
(`evals/questions.jsonl`, built from `evals/ground_truth.json`, seed 42).

- **Hit:** a retrieved chunk from the gold contract **and** the gold page.
- **Recall@5:** share of questions with a hit in the top 5. **MRR@10:** mean of 1/rank of the
  first hit within the top 10 (0 if none). **Doc recall@5:** same as recall@5 but only the
  contract must match (looser).
- Latency is the whole search call: query embedding plus the SQL.
- Numbers from the fake embedder are never written here; they only check the harness.

| Date | Git SHA | Label | Mode | Embedder | Recall@5 | MRR@10 | Doc recall@5 | p50 ms | p95 ms |
|---|---|---|---|---|---|---|---|---|---|
<!-- evals:end -->

## Reproduce

From `backend/`, with the stack running and `GEMINI_API_KEY` set (free tier; synthetic data only):

```bash
uv run python ../evals/generate_corpus.py      # 25 contracts + 300 invoices -> evals/corpus (git-ignored)
uv run python ../evals/build_questions.py      # 90 questions -> evals/questions.jsonl
uv run python ../evals/load_corpus.py          # upload and wait until every document is ready
uv run python ../evals/run_evals.py --modes vector --label baseline
```

Set `EMBEDDING_MIN_INTERVAL_S=2` and `EXTRACTION_MIN_INTERVAL_S=6.5` on the worker to stay inside
free-tier per-minute limits (check your quotas in AI Studio); invoice extraction is the slow part.

**Status:** harness verified end to end with the fake embedder; the real Gemini baseline row is
still to be recorded.
