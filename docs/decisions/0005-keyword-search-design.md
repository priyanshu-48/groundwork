# 0005: How the keyword leg of hybrid search works
- **Context:** SPEC §6.4 says `websearch_to_tsquery` + `ts_rank_cd`. Used as is, it failed on our data in three ways.
- **OR, not AND:** `websearch_to_tsquery` ANDs terms, so a natural question fails if one word is absent from the page. We swap ` & ` for ` | ` and let `ts_rank_cd` rank pages matching more terms first.
- **Hyphenated identifiers:** Postgres tokenizes `V02-2025-0003` differently depending on neighbouring words (`-2025` becomes a signed number), so exact IDs matched in some invoice layouts and not others. The `tsv` column now splits word-internal hyphens into spaces (migration 0005) and the query gets the same treatment, with each identifier quoted so it must match as an adjacent phrase.
- **No IDF:** `ts_rank_cd` does not weight rare terms, so a chunk repeating "invoice" outranked the one chunk holding the exact ID. Query tokens containing a digit (IDs, dates, amounts) therefore add a boost in `ORDER BY` before `ts_rank_cd`.
- **Limits:** a heuristic, not BM25. Real BM25 (or `pg_search`) would handle term rarity properly; revisit if the keyword leg becomes the bottleneck.
