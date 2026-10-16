"""Opt-in: loads the real cross-encoder (downloads ~22 MB on first use). CI skips it."""

import os
import uuid

import pytest

from app.repositories.chunks import Hit
from app.services.rerank import FlashRankReranker

pytestmark = pytest.mark.skipif(
    os.environ.get("RUN_MODEL_TESTS") != "1", reason="set RUN_MODEL_TESTS=1 to run model tests"
)


async def test_real_model_puts_the_relevant_passage_first() -> None:
    def hit(text: str) -> Hit:
        return Hit(uuid.uuid4(), uuid.uuid4(), "f.pdf", 1, text, 0.0)

    hits = [
        hit("The office kitchen is cleaned every Friday afternoon."),
        hit("Either party may end this Agreement by giving sixty days written notice."),
        hit("Parking spaces are assigned by seniority."),
    ]
    rr = FlashRankReranker(cache_dir=".flashrank")
    out = await rr.rerank("How much notice is needed to terminate the contract?", hits, top_k=3)
    assert out[0].content.startswith("Either party may end")
    assert out[0].score > out[-1].score
