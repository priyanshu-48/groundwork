# 0013: Query-embedding cache
- **Context:** the free embedding quota is ~1000 requests/day and every search embeds the query, so repeated questions burned quota and added ~450 ms.
- **Decision:** a bounded in-process LRU (1000 entries) in front of the embedder for `task="query"` only, keyed by model + text. Document embeddings are never cached. Concurrent identical misses share one call. Failures are not cached.
- **Why no TTL:** the embedding of fixed text under a fixed model never changes; changing the model changes the key.
- **Limits:** per process (lost on restart, duplicated across processes); keys hold query text in memory only, never written to disk or logs. The load test reports cold and warm separately so the cache does not flatter the numbers.
