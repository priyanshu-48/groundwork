"""Split page text into overlapping chunks that never cross a page boundary, so every chunk keeps
an exact page number for citations.

Token counts are approximated (1 token ~ 0.75 word) because a real tokenizer would be a heavy
dependency and the embedding model counts differently anyway; see docs/decisions/0002."""

import math
import re
from dataclasses import dataclass

WORDS_PER_TOKEN = 0.75
CHUNK_TOKENS = 500
OVERLAP_TOKENS = 60
DEFAULT_MAX_WORDS = int(CHUNK_TOKENS * WORDS_PER_TOKEN)  # 375
DEFAULT_OVERLAP_WORDS = int(OVERLAP_TOKENS * WORDS_PER_TOKEN)  # 45

_WORD = re.compile(r"\S+")


@dataclass(frozen=True)
class TextChunk:
    ord: int
    page: int
    content: str
    token_count: int


def chunk_pages(
    pages: list[str],
    max_words: int = DEFAULT_MAX_WORDS,
    overlap_words: int = DEFAULT_OVERLAP_WORDS,
) -> list[TextChunk]:
    """pages[0] is page 1. Chunks are slices of the original text between word boundaries, so
    newlines and spacing (invoice tables) survive. The overlap keeps a sentence that straddles a
    chunk edge retrievable from either side."""
    step = max_words - overlap_words
    out: list[TextChunk] = []
    for page_no, text in enumerate(pages, start=1):
        spans = [m.span() for m in _WORD.finditer(text)]
        start = 0
        while spans:
            end = min(start + max_words, len(spans))
            content = text[spans[start][0] : spans[end - 1][1]]
            tokens = math.ceil((end - start) / WORDS_PER_TOKEN)
            out.append(TextChunk(len(out), page_no, content, tokens))
            if end == len(spans):
                break
            start += step
    return out
