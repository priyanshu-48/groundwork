"""Evidence that the search queries use their indexes, and what iterative HNSW scan fixes.

Builds a scratch database next to the dev database (30 orgs x 1000 synthetic chunks), runs
EXPLAIN (ANALYZE, BUFFERS) for the vector and keyword queries, and compares how many rows a
selective org filter returns with hnsw.iterative_scan off vs relaxed_order. Writes the result to
docs/decisions/0006-search-explain-analyze.md and drops the scratch database. No API calls.

Run (from backend/, Postgres up):
    DATABASE_URL=postgresql+asyncpg://groundwork:groundwork@localhost:5433/groundwork \\
        uv run python ../evals/explain_search.py
"""

import asyncio
import os
import random
import sys
import uuid
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for p in (ROOT, ROOT / "backend"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from sqlalchemy import text  # noqa: E402
from sqlalchemy.engine import make_url  # noqa: E402
from sqlalchemy.ext.asyncio import create_async_engine  # noqa: E402

SCRATCH = "groundwork_explain"
ORGS, PER_ORG = 30, 1000


def _vec(rng: random.Random) -> str:
    return "[" + ",".join(f"{rng.uniform(-1, 1):.4f}" for _ in range(768)) + "]"


async def _explain(conn, sql: str) -> str:  # type: ignore[no-untyped-def]
    rows = (await conn.execute(text("EXPLAIN (ANALYZE, BUFFERS) " + sql))).scalars().all()
    return "\n".join(rows)


async def main() -> None:
    base = make_url(os.environ["DATABASE_URL"])
    admin = create_async_engine(base.set(database="postgres"), isolation_level="AUTOCOMMIT")
    async with admin.connect() as c:
        await c.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH}"))
        await c.execute(text(f"CREATE DATABASE {SCRATCH}"))
    scratch_url = base.set(database=SCRATCH).render_as_string(hide_password=False)

    os.environ["DATABASE_URL"] = scratch_url  # alembic's env.py reads settings from the environment
    from alembic import command
    from alembic.config import Config

    cfg = Config(str(ROOT / "backend" / "alembic.ini"))
    cfg.set_main_option("script_location", str(ROOT / "backend" / "alembic"))
    await asyncio.to_thread(command.upgrade, cfg, "head")

    engine = create_async_engine(scratch_url)
    rng = random.Random(42)
    vocab = [
        "".join(rng.choices("abcdefghijklmnopqrstuvwxyz", k=rng.randint(4, 9))) for _ in range(2000)
    ]
    org_ids = [uuid.uuid4() for _ in range(ORGS)]
    print(f"loading {ORGS * PER_ORG} synthetic chunks ...")
    async with engine.begin() as c:
        await c.execute(text("SELECT setseed(0.42)"))
        for i, org in enumerate(org_ids):
            doc = uuid.uuid4()
            await c.execute(text("INSERT INTO orgs (id, name) VALUES (:i, 'o')"), {"i": org})
            await c.execute(
                text(
                    "INSERT INTO documents (id, org_id, filename, s3_key, sha256, kind, status) "
                    "VALUES (:d, :o, 'f.pdf', 'k', :sha, 'contract', 'ready')"
                ),
                {"d": doc, "o": org, "sha": f"{i:064d}"},
            )
            await c.execute(
                text(
                    """
                INSERT INTO chunks (id, org_id, document_id, ord, page, content, token_count, embedding)
                SELECT gen_random_uuid(), :o, :d, n, 1 + n % 5,
                       (SELECT string_agg((CAST(:vocab AS text[]))[1 + floor(random() * 2000)::int], ' ')
                        FROM generate_series(1, 60) WHERE n IS NOT NULL),
                       80,
                       (SELECT array_agg(random() - 0.5) FROM generate_series(1, 768)
                        WHERE n IS NOT NULL)::vector
                FROM generate_series(1, :per) AS n
                """
                ),
                {"o": org, "d": doc, "vocab": vocab, "per": PER_ORG},
            )
        # a single needle chunk for the keyword plan
        await c.execute(
            text(
                "UPDATE chunks SET content = content || ' V07-2025-0003 invoice' WHERE id = "
                "(SELECT id FROM chunks WHERE org_id = :o LIMIT 1)"
            ),
            {"o": org_ids[0]},
        )
    print("analyzing ...")
    async with engine.connect() as c:
        await c.execution_options(isolation_level="AUTOCOMMIT")
        await c.execute(text("ANALYZE chunks"))
        versions = {
            "postgres": (await c.execute(text("SHOW server_version"))).scalar(),
            "pgvector": (
                await c.execute(text("SELECT extversion FROM pg_extension WHERE extname='vector'"))
            ).scalar(),
            "ef_search": (await c.execute(text("SHOW hnsw.ef_search"))).scalar(),
        }

    org = org_ids[3]
    qv = _vec(rng)
    vector_sql = (
        "SELECT c.id, d.filename, c.page, c.embedding <=> CAST('{v}' AS vector) AS distance "
        "FROM chunks c JOIN documents d ON d.id = c.document_id "
        "WHERE c.org_id = '{o}' ORDER BY c.embedding <=> CAST('{v}' AS vector) LIMIT 5"
    ).format(v=qv, o=org)
    keyword_sql = (
        "SELECT c.id, ts_rank_cd(c.tsv, q.query) AS score FROM chunks c "
        "CROSS JOIN (SELECT replace(websearch_to_tsquery('english', 'V07-2025-0003 invoice')::text, "
        "' & ', ' | ')::tsquery AS query) q "
        "WHERE c.org_id = '{o}' AND c.tsv @@ q.query ORDER BY score DESC LIMIT 20"
    ).format(o=org_ids[0])
    keyword_sql = keyword_sql.replace("V07-2025-0003", "V07 2025 0003")  # same prep as the app

    report: dict[str, str] = {}
    counts: dict[str, int] = {}
    async with engine.connect() as c:
        for label, setting in (("off", "off"), ("on", "relaxed_order")):
            async with c.begin():
                await c.execute(text(f"SET LOCAL hnsw.iterative_scan = {setting}"))
                counts[label] = len((await c.execute(text(vector_sql))).all())
                report[f"vector_{label}"] = await _explain(c, vector_sql)
        async with c.begin():
            await c.execute(text("SET LOCAL hnsw.iterative_scan = relaxed_order"))
            await c.execute(text("SET LOCAL enable_seqscan = off"))
            report["vector_forced_index"] = await _explain(c, vector_sql)
        async with c.begin():
            report["keyword"] = await _explain(c, keyword_sql)
        async with c.begin():
            await c.execute(text("SET LOCAL enable_seqscan = off"))
            report["keyword_forced_index"] = await _explain(c, keyword_sql)

    uses_hnsw = "ix_chunks_embedding_hnsw" in report["vector_on"]
    uses_gin = "ix_chunks_tsv" in report["keyword"]
    out = f"""# 0006: EXPLAIN ANALYZE of the search queries (generated, do not edit by hand)
Generated {date.today().isoformat()} by `evals/explain_search.py`. Scratch DB with {ORGS} orgs x {PER_ORG}
random 768-d chunks ({ORGS * PER_ORG} rows), postgres {versions["postgres"]}, pgvector {versions["pgvector"]},
`hnsw.ef_search` = {versions["ef_search"]}. Random vectors, so this shows plans and the filter effect, not
recall quality (that is `docs/evals.md`).

## What this shows
- Vector query planner choice at this size: **{"HNSW index" if uses_hnsw else "not the HNSW index (see below)"}**.
- Keyword query planner choice: **{"GIN index on tsv" if uses_gin else "not the GIN index (see below)"}**.
- Org filter selectivity is 1/{ORGS}. Rows returned for LIMIT 5 with `hnsw.iterative_scan`:
  **off = {counts["off"]}**, **relaxed_order = {counts["on"]}**. HNSW fetches only `ef_search` candidates and the
  org filter is applied afterwards, so a selective filter can leave fewer than k rows; iterative scan keeps
  scanning until k rows survive (the app sets it with SET LOCAL on every search).

## Vector query, iterative_scan = relaxed_order
```
{report["vector_on"]}
```

## Vector query, iterative_scan = off
```
{report["vector_off"]}
```

## Vector query with sequential scans disabled (proves the HNSW index is usable)
```
{report["vector_forced_index"]}
```

## Keyword query (OR tsquery, GIN on tsv)
```
{report["keyword"]}
```

## Keyword query with sequential scans disabled
```
{report["keyword_forced_index"]}
```
"""
    (ROOT / "docs" / "decisions" / "0006-search-explain-analyze.md").write_text(
        out, encoding="utf8"
    )
    print(f"vector uses HNSW: {uses_hnsw}; keyword uses GIN: {uses_gin}; rows off/on: {counts}")

    await engine.dispose()
    async with admin.connect() as c:
        await c.execute(text(f"DROP DATABASE IF EXISTS {SCRATCH}"))
    await admin.dispose()


if __name__ == "__main__":
    asyncio.run(main())
