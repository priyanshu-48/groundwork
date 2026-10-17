import logging
from dataclasses import dataclass
from typing import Any

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.agent.llm import GeminiLLM
from app.config import Settings, model_chain_names
from app.db import make_engine
from app.services.embeddings import (
    EmbeddingProvider,
    FakeEmbeddingProvider,
    GeminiEmbeddingProvider,
)
from app.services.extraction import FakeInvoiceExtractor, GeminiInvoiceExtractor, InvoiceExtractor
from app.services.gemini import ModelChain, Throttle, make_client
from app.services.rerank import FlashRankReranker
from app.services.storage import make_s3

log = logging.getLogger(__name__)


@dataclass(frozen=True)
class Deps:
    """Everything a job handler needs, passed explicitly so tests can swap in fakes."""

    maker: async_sessionmaker[Any]
    s3: Any
    bucket: str
    embedder: EmbeddingProvider
    extractor: InvoiceExtractor
    settings: Settings
    reranker: Any = None  # app.services.rerank.Reranker, built only when a mode needs it
    llm: Any = None  # app.agent.llm.LLM; None in fake mode (agent needs a scripted FakeLLM)


def build_deps(s: Settings) -> tuple[Deps, AsyncEngine]:
    engine = make_engine(s.database_url)
    if s.ai_provider == "gemini":
        if not s.gemini_api_key:
            # Refuse rather than quietly using fake embeddings that would poison the index.
            raise SystemExit(
                "AI_PROVIDER=gemini but GEMINI_API_KEY is not set (use AI_PROVIDER=fake for dev)"
            )
        client = make_client(s)
        embedder: EmbeddingProvider = GeminiEmbeddingProvider(
            client,
            s.embedding_model,
            s.embedding_dims,
            throttle=Throttle(s.embedding_min_interval_s),
        )
        chain = ModelChain(model_chain_names(s))
        extractor: InvoiceExtractor = GeminiInvoiceExtractor(
            client, chain, Throttle(s.extraction_min_interval_s)
        )
        llm: GeminiLLM | None = GeminiLLM(client, chain, Throttle(s.agent_min_interval_s))
    else:
        log.warning("AI_PROVIDER=fake: embeddings and extraction are NOT real")
        llm = None
        embedder, extractor = FakeEmbeddingProvider(s.embedding_dims), FakeInvoiceExtractor()
    deps = Deps(
        maker=async_sessionmaker(engine, expire_on_commit=False),
        s3=make_s3(s),
        bucket=s.s3_bucket,
        embedder=embedder,
        extractor=extractor,
        settings=s,
        reranker=FlashRankReranker(s.rerank_model, s.rerank_cache_dir)
        if s.search_mode == "hybrid_rerank"
        else None,
        llm=llm,
    )
    return deps, engine
