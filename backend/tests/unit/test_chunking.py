import math

from app.services.chunking import chunk_pages
from tests.helpers import words


def test_short_page_is_one_chunk() -> None:
    chunks = chunk_pages([words(50)])
    assert len(chunks) == 1
    assert (chunks[0].ord, chunks[0].page) == (0, 1)


def test_never_crosses_a_page_boundary() -> None:
    chunks = chunk_pages([words(500, "a"), words(500, "b")], max_words=100, overlap_words=10)
    assert {c.page for c in chunks} == {1, 2}
    for c in chunks:
        prefix = "a" if c.page == 1 else "b"
        assert all(w.startswith(prefix) for w in c.content.split())


def test_consecutive_chunks_overlap_and_respect_size() -> None:
    chunks = chunk_pages([words(1000)], max_words=100, overlap_words=10)
    assert all(len(c.content.split()) <= 100 for c in chunks)
    for prev, nxt in zip(chunks, chunks[1:], strict=False):
        assert prev.content.split()[-10:] == nxt.content.split()[:10]
    assert chunks[-1].content.split()[-1] == "w999"  # nothing lost at the tail


def test_ord_is_contiguous_across_pages() -> None:
    chunks = chunk_pages([words(300, "a"), words(300, "b")], max_words=100, overlap_words=10)
    assert [c.ord for c in chunks] == list(range(len(chunks)))


def test_blank_pages_are_skipped_but_page_numbers_stay_true() -> None:
    chunks = chunk_pages(["", "  \n ", words(10)])
    assert [(c.ord, c.page) for c in chunks] == [(0, 3)]


def test_newlines_are_preserved() -> None:
    (c,) = chunk_pages(["Item  Qty\nWidget  3"])
    assert c.content == "Item  Qty\nWidget  3"


def test_deterministic() -> None:
    pages = [words(900), words(400, "b")]
    assert chunk_pages(pages) == chunk_pages(pages)


def test_default_window_is_about_500_tokens_with_60_overlap() -> None:
    chunks = chunk_pages([words(1000)])
    assert 480 <= chunks[0].token_count <= 500
    assert chunks[0].token_count == math.ceil(len(chunks[0].content.split()) / 0.75)
