"""POST /search: the same retrieval the agent's search tool uses, as a plain HTTP endpoint."""

from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from app.agent.loop import snippet
from app.api.deps import current_user
from app.models.document import DocKind
from app.services.ratelimit import Limits, get_limits, too_many
from app.services.retrieval import search_documents
from app.services.security import Principal
from app.worker.deps import Deps

router = APIRouter(tags=["search"])


class SearchIn(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    kind: Literal["invoice", "contract"] | None = None
    top_k: int = Field(default=5, ge=1, le=10)


class SearchHit(BaseModel):
    filename: str
    page: int
    score: float
    snippet: str


class SearchOut(BaseModel):
    mode: str
    hits: list[SearchHit]


@router.post("/search", response_model=SearchOut)
async def search(
    body: SearchIn,
    request: Request,
    p: Principal = Depends(current_user),
    limits: Limits = Depends(get_limits),
) -> SearchOut:
    deps: Deps | None = getattr(request.app.state, "agent_deps", None)
    if deps is None:
        raise HTTPException(503, "Search is not configured on this server")
    if (wait := limits.search.check(str(p.org_id))) is not None:
        raise too_many(wait, "searches")
    s = deps.settings
    mode = s.search_mode if s.search_mode != "hybrid_rerank" or deps.reranker else "hybrid"
    async with deps.maker() as session:
        hits = await search_documents(
            session,
            deps.embedder,
            p.org_id,
            body.query,
            mode=mode,
            kind=DocKind(body.kind) if body.kind else None,
            top_k=body.top_k,
            reranker=deps.reranker,
            candidate_k=s.candidate_k,
            rrf_k=s.rrf_k,
        )
    return SearchOut(
        mode=mode,
        hits=[
            SearchHit(
                filename=h.filename, page=h.page, score=h.score, snippet=snippet(h.content, 240)
            )
            for h in hits
        ],
    )
