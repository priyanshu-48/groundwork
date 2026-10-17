"""The agent's three tools. Each is a Pydantic argument model plus an async function.

Security shape: the model only ever supplies *values*. org_id comes from the AgentContext (set by
the server from the caller's token), argument models forbid unknown fields so an injected
"org_id" is rejected, SQL lives in repositories, and chunk ids are exposed as short per-run refs
so there is nothing to guess."""

import json
import re
import uuid
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Annotated, Any, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    ValidationError,
    model_validator,
)
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.agent.llm import ToolSpec
from app.config import Settings
from app.models.document import DocKind
from app.repositories import chunks as chunks_repo
from app.repositories import contracts as contracts_repo
from app.repositories import invoices as invoices_repo
from app.repositories.chunks import Hit
from app.services.embeddings import EmbeddingError, EmbeddingProvider
from app.services.rerank import Reranker
from app.services.retrieval import search_documents

SEARCH_CHARS_PER_CHUNK = 1200  # search shows enough to answer most questions; read_chunks shows all


@dataclass
class AgentContext:
    """Everything a tool may touch, fixed by the server before the model says anything."""

    org_id: uuid.UUID
    maker: async_sessionmaker[Any]
    embedder: EmbeddingProvider
    settings: Settings
    reranker: Reranker | None = None
    refs: dict[str, Hit] = field(default_factory=dict)
    _by_chunk: dict[uuid.UUID, str] = field(default_factory=dict)

    def register(self, hit: Hit) -> str:
        """Short stable label (C1, C2, ...) for a chunk this run has retrieved."""
        if hit.chunk_id not in self._by_chunk:
            ref = f"C{len(self.refs) + 1}"
            self._by_chunk[hit.chunk_id] = ref
            self.refs[ref] = hit
        return self._by_chunk[hit.chunk_id]


@dataclass(frozen=True)
class ToolOutput:
    text: str
    preview: str
    is_error: bool = False


class ToolError(Exception):
    """A problem the model can fix by calling again; the message is shown to it."""


class _Args(BaseModel):
    model_config = ConfigDict(extra="forbid")


class SearchArgs(_Args):
    query: Annotated[str, StringConstraints(min_length=1, max_length=500)]
    kind: Literal["invoice", "contract"] | None = None
    top_k: int = Field(5, ge=1, le=8)


class ReadArgs(_Args):
    refs: list[Annotated[str, StringConstraints(pattern=r"^C\d{1,4}$")]] = Field(
        min_length=1, max_length=5
    )


class QueryInvoicesArgs(_Args):
    vendor: Annotated[str, StringConstraints(max_length=200)] | None = None
    vendors: list[Annotated[str, StringConstraints(min_length=1, max_length=200)]] | None = Field(
        None, max_length=10
    )
    date_from: date | None = None
    date_to: date | None = None
    payment_terms_days: int | None = Field(None, ge=1, le=365)
    aggregate: Literal["sum", "count", "list"]
    group_by_vendor: bool = False
    limit: int = Field(20, ge=1, le=50)

    @model_validator(mode="after")
    def _consistent(self) -> "QueryInvoicesArgs":
        if self.vendor and self.vendors:
            raise ValueError("pass either vendor or vendors, not both")
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must not be after date_to")
        if self.aggregate == "list" and self.group_by_vendor:
            raise ValueError("group_by_vendor works with sum or count, not list")
        return self


class QueryContractsArgs(_Args):
    vendor: Annotated[str, StringConstraints(max_length=200)] | None = None
    payment_terms_days: int | None = Field(None, ge=1, le=365)
    auto_renewal: bool | None = None
    governing_law: Annotated[str, StringConstraints(max_length=100)] | None = None
    limit: int = Field(25, ge=1, le=50)


# ------------------------------------------------------------------ rendering


def escape_document_text(text: str) -> str:
    """Stop retrieved text from closing or opening our <document> wrapper."""
    return re.sub(r"<(/?)(document)", r"&lt;\1\2", text, flags=re.IGNORECASE)


def _attr(v: str) -> str:
    return re.sub(r'["<>\n]', "'", v)


def doc_block(ref: str, hit: Hit, limit: int | None = None) -> str:
    body = (
        hit.content if limit is None or len(hit.content) <= limit else hit.content[:limit] + " ..."
    )
    return (
        f'<document ref="{ref}" file="{_attr(hit.filename)}" page="{hit.page}">\n'
        f"{escape_document_text(body)}\n</document>"
    )


def truncate(text: str, budget: int) -> str:
    if len(text) <= budget:
        return text
    return text[:budget] + "\n[output truncated: narrow the query or use read_chunks]"


# ------------------------------------------------------------------ tool bodies


async def search_tool(ctx: AgentContext, a: SearchArgs) -> ToolOutput:
    s = ctx.settings
    mode = s.search_mode
    if mode == "hybrid_rerank" and ctx.reranker is None:
        mode = "hybrid"  # configured reranker missing: degrade to the best model-free mode
    async with ctx.maker() as session:
        hits = await search_documents(
            session,
            ctx.embedder,
            ctx.org_id,
            a.query,
            mode=mode,
            kind=DocKind(a.kind) if a.kind else None,
            top_k=a.top_k,
            reranker=ctx.reranker,
            candidate_k=s.candidate_k,
            rrf_k=s.rrf_k,
        )
    if not hits:
        return ToolOutput("No results.", "no results")
    blocks = [doc_block(ctx.register(h), h, SEARCH_CHARS_PER_CHUNK) for h in hits]
    head = f"{len(hits)} results, best first. Use read_chunks for full text.\n"
    return ToolOutput(
        truncate(head + "\n".join(blocks), s.tool_result_char_budget),
        f"{len(hits)} results: "
        + ", ".join(f"{ctx.register(h)}={h.filename} p{h.page}" for h in hits),
    )


async def read_tool(ctx: AgentContext, a: ReadArgs) -> ToolOutput:
    unknown = [r for r in a.refs if r not in ctx.refs]
    if unknown:
        raise ToolError(f"unknown refs {unknown}; use refs returned by earlier tool calls")
    ids = [ctx.refs[r].chunk_id for r in a.refs]
    async with ctx.maker() as session:
        found = {h.chunk_id: h for h in await chunks_repo.fetch_by_ids(session, ctx.org_id, ids)}
    blocks = [
        doc_block(r, found[ctx.refs[r].chunk_id]) for r in a.refs if ctx.refs[r].chunk_id in found
    ]
    if not blocks:
        raise ToolError("those chunks are no longer available")
    return ToolOutput(
        truncate("\n".join(blocks), ctx.settings.tool_result_char_budget),
        f"read {', '.join(a.refs)}",
    )


def _jsonable(v: Any) -> Any:
    if isinstance(v, Decimal):
        return str(v)  # money stays a string end to end
    if isinstance(v, date):
        return v.isoformat()
    if isinstance(v, uuid.UUID):
        return str(v)
    return v


async def invoices_tool(ctx: AgentContext, a: QueryInvoicesArgs) -> ToolOutput:
    vendors = a.vendors or ([a.vendor] if a.vendor else [])
    async with ctx.maker() as session:
        rows = await invoices_repo.aggregate(
            session,
            ctx.org_id,
            aggregate=a.aggregate,
            vendors=vendors,
            date_from=a.date_from,
            date_to=a.date_to,
            group_by_vendor=a.group_by_vendor,
            limit=a.limit,
            payment_terms_days=a.payment_terms_days,
        )
        firsts = (
            await chunks_repo.first_chunks(session, ctx.org_id, [r["document_id"] for r in rows])
            if a.aggregate == "list" and rows
            else {}
        )
    out_rows: list[dict[str, Any]] = []
    for r in rows:
        row = {k: _jsonable(v) for k, v in r.items() if k != "document_id"}
        doc_id = r.get("document_id")
        if doc_id is not None and (chunk := firsts.get(doc_id)) is not None:
            row["ref"] = ctx.register(chunk)
        out_rows.append(row)
    payload = {
        "aggregate": a.aggregate,
        "rows": out_rows,
        "note": "Only invoices that passed validation are counted. Sums are per currency.",
    }
    if not out_rows:
        payload["note"] = "No matching invoices (vendor names match by substring, dates inclusive)."
    text = json.dumps(payload)
    return ToolOutput(
        truncate(text, ctx.settings.tool_result_char_budget), f"{a.aggregate}: {len(out_rows)} rows"
    )


async def contracts_tool(ctx: AgentContext, a: QueryContractsArgs) -> ToolOutput:
    async with ctx.maker() as session:
        rows = await contracts_repo.query(
            session,
            ctx.org_id,
            vendor=a.vendor,
            payment_terms_days=a.payment_terms_days,
            auto_renewal=a.auto_renewal,
            governing_law=a.governing_law,
            limit=a.limit,
        )
        firsts = (
            await chunks_repo.first_chunks(session, ctx.org_id, [r["document_id"] for r in rows])
            if rows
            else {}
        )
    out_rows: list[dict[str, Any]] = []
    for r in rows:
        row = {k: _jsonable(v) for k, v in r.items() if k != "document_id"}
        if (chunk := firsts.get(r["document_id"])) is not None:
            row["ref"] = ctx.register(chunk)  # the contract's opening page, for traceability
        out_rows.append(row)
    note = "Vendors whose contract matches. Only contracts that passed validation are listed."
    if not out_rows:
        note = "No matching contracts (vendor and law match by substring)."
    text = json.dumps({"rows": out_rows, "note": note})
    return ToolOutput(
        truncate(text, ctx.settings.tool_result_char_budget), f"contracts: {len(out_rows)} rows"
    )


# ------------------------------------------------------------------ registry


@dataclass(frozen=True)
class Tool:
    name: str
    description: str
    args_model: type[BaseModel]
    run: Callable[[AgentContext, Any], Awaitable[ToolOutput]]


TOOLS: dict[str, Tool] = {
    t.name: t
    for t in (
        Tool(
            "search_documents",
            "Search the company's contracts and invoices. Returns the best matching passages, "
            "each with a ref like C1 to cite. Works for meaning (paraphrases) and for exact "
            "identifiers such as invoice numbers.",
            SearchArgs,
            search_tool,
        ),
        Tool(
            "read_chunks",
            "Return the full text of passages you already retrieved, by ref (up to 5).",
            ReadArgs,
            read_tool,
        ),
        Tool(
            "query_contracts",
            "List vendors by structured contract terms: payment_terms_days (net-30 means 30), "
            "auto_renewal, governing_law (substring), or one vendor. Returns each vendor's payment "
            "terms, late fee % per month, termination notice days, auto-renewal, liability cap "
            "and governing law. Use this for 'which vendors have ...' questions; unlike search it "
            "returns every match.",
            QueryContractsArgs,
            contracts_tool,
        ),
        Tool(
            "query_invoices",
            "Exact invoice totals, counts or lists from the structured invoice table. Filter by "
            "vendor name(s), an inclusive issue-date range, and payment_terms_days (only invoices "
            "from vendors whose contract has those terms, so net-30 vendors = 30). aggregate=sum "
            "gives totals per currency; group_by_vendor=true gives one row per vendor.",
            QueryInvoicesArgs,
            invoices_tool,
        ),
    )
}


def specs() -> list[ToolSpec]:
    return [
        ToolSpec(t.name, t.description, t.args_model.model_json_schema()) for t in TOOLS.values()
    ]


def _short(e: ValidationError) -> str:
    return "; ".join(
        f"{'.'.join(map(str, x['loc'])) or 'arguments'}: {x['msg']}" for x in e.errors()
    )


async def execute(ctx: AgentContext, name: str, raw_args: dict[str, Any]) -> ToolOutput:
    """Validate and run one tool call. Problems the model can fix come back as error output."""
    tool = TOOLS.get(name)
    if tool is None:
        msg = f"unknown tool {name!r}; available: {', '.join(TOOLS)}"
        return ToolOutput(f"Error: {msg}", msg, True)
    try:
        args = tool.args_model.model_validate(raw_args)
        return await tool.run(ctx, args)
    except ValidationError as e:
        msg = f"invalid arguments: {_short(e)}"
        return ToolOutput(f"Error: {msg}", msg, True)
    except ToolError as e:
        return ToolOutput(f"Error: {e}", str(e), True)
    except EmbeddingError:
        # e.g. the embedding quota is used up. The model can still try the SQL tool, so this is a
        # tool result, not a crashed run.
        msg = "search is temporarily unavailable; try query_invoices or answer from what you have"
        return ToolOutput(f"Error: {msg}", msg, True)
