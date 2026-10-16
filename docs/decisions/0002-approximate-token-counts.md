# 0002: Approximate token counts for chunking
- **Context:** SPEC §6.3 wants ~500-token chunks with 60 overlap, never crossing a page.
- **Decision:** Count words and treat 1 token as 0.75 word (375-word window, 45-word overlap); no tokenizer dependency.
- **Why:** Gemini's tokenizer is not available locally anyway; chunk size only needs to be roughly right for retrieval, and word windows are deterministic and cheap.
- **Ceiling:** Dense text (numbers, tables) tokenizes to more tokens per word, so chunks can exceed 500 real tokens. Still far below the 2048-token embedding limit. Revisit if evals show truncation.
