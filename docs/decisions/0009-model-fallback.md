# 0009: Model fallback chain for generation, never for embeddings
- **Context:** free-tier quotas are per model (one showed 20 generate_content requests per day), and a full eval needs hundreds of calls.
- **Decision:** `GEMINI_MODELS=a,b,c` is tried in order. A model is skipped until its `retryDelay` after a quota 429 (or 60 s after a 5xx, forever after a 404). 400/401/403 are raised, not retried elsewhere, because another model would fail the same way. If every model is unavailable the run ends with status `error` and a clear message.
- **Embeddings never fall back:** vectors from a different embedding model are not comparable, so mixing them silently breaks search.
- **Consequences:** the answering model is stored in `agent_runs.model` and in eval results, because answers differ between models; the chain is part of the eval cache key.
- **Not verified yet:** the function-declaration schema, the batched-extraction schema and thought-signature replay have only been tested against stubs. The first live run may need small schema adjustments.
