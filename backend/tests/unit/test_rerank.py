import threading
import uuid
from typing import Any

from app.repositories.chunks import Hit
from app.services.rerank import FakeReranker, FlashRankReranker


def hit(text: str, score: float = 0.0) -> Hit:
    return Hit(uuid.uuid4(), uuid.uuid4(), "f.pdf", 1, text, score)


async def test_fake_reranker_orders_by_word_overlap_and_caps_top_k() -> None:
    hits = [hit("banana smoothie"), hit("late payment penalty clause"), hit("penalty only")]
    out = await FakeReranker().rerank("late payment penalty", hits, top_k=2)
    assert [h.content for h in out] == ["late payment penalty clause", "penalty only"]
    assert out[0].score > out[1].score


class StubRanker:
    def __init__(self) -> None:
        self.thread: threading.Thread | None = None
        self.passages: list[dict[str, Any]] = []

    def rerank(self, request: Any) -> list[dict[str, Any]]:
        self.thread = threading.current_thread()
        self.passages = request.passages
        # deliberately unsorted: the adapter must not rely on the library's ordering
        return [
            {"id": p["id"], "text": p["text"], "score": float(len(p["text"]))}
            for p in request.passages
        ]


async def test_flashrank_adapter_maps_ids_sorts_by_score_and_stays_off_the_loop() -> None:
    stub = StubRanker()
    hits = [hit("aa"), hit("aaaa"), hit("a")]
    rr = FlashRankReranker(ranker=stub)
    out = await rr.rerank("q", hits, top_k=2)
    assert [h.content for h in out] == ["aaaa", "aa"]
    assert [h.chunk_id for h in out] == [hits[1].chunk_id, hits[0].chunk_id]
    assert out[0].score == 4.0
    assert len(stub.passages) == 3
    assert stub.thread is not threading.main_thread()


async def test_empty_candidates_skip_the_model() -> None:
    stub = StubRanker()
    assert await FlashRankReranker(ranker=stub).rerank("q", [], top_k=5) == []
    assert stub.thread is None
