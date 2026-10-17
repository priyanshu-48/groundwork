# Groundwork: Build Spec

**A document Q&A agent that cites its sources, over a company's invoices and contracts**
FastAPI · PostgreSQL + pgvector · Hybrid RAG + reranking · Tool-calling agent · React/TypeScript · AWS

> How to use this file: put it in the root of a new repo as `SPEC.md`. Copy the "CLAUDE.md" section below into `CLAUDE.md`. Then work through the milestones one at a time with Claude Code, one session per milestone, starting each session in plan mode.

---

## 1. What you are building (the 30-second pitch)

A finance team uploads their vendor **invoices and contracts** as PDFs. They then ask questions in plain English:

| Question | What the system must do |
|---|---|
| "What's the late-payment penalty in our Acme contract?" | **RAG:** find the right clause, answer, and cite the page |
| "How much did we pay Acme in Q2 2025?" | **Tool call:** run a safe, parameterised SQL aggregate over the invoice fields extracted at upload |
| "Which vendor on net-45 terms billed us the most in March?" | **Multi-step agent:** search the contracts for net-45, then query the invoices, then combine |

Every answer shows **citations** (document, page, snippet) and a "steps" panel that shows each tool the agent called.

**Why this project:** it closes the gaps that kept appearing in your applications, which were RAG, embeddings, vector search, tool calling, agents, Python/FastAPI and AWS. It also keeps your strengths: Postgres tuning, reliability (idempotency, retries, crash safety), testing and React/TS. The finance domain lines up directly with billing companies like Zenskar.

**Ground rule for interviews:** Claude Code writes code fast, but **you must be able to explain every file**. After each milestone, read the diff and ask Claude Code "explain why this is designed this way and what breaks if I change X" until you could rebuild it yourself.

---

## 2. Tech stack (fixed, so don't let Claude Code swap these)

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.12, managed with `uv` | Fast installs and a single lockfile |
| API | FastAPI + Pydantic v2 | Asked for in the job descriptions; async; generates OpenAPI docs |
| DB access | SQLAlchemy 2.0 (async) + asyncpg + Alembic | Industry standard, with real migrations |
| Database | PostgreSQL 16 + **pgvector ≥ 0.8** | One database for relational data, vectors and full-text search |
| Job queue | **Postgres table using `SELECT … FOR UPDATE SKIP LOCKED`** | No extra infrastructure, transactional, and a strong interview topic |
| File storage | **S3** (MinIO locally, through the same boto3 code) | AWS requirement; local dev runs the same code path |
| PDF parsing | PyMuPDF (`pymupdf`) | Fast and gives page-level text |
| Embeddings | Gemini `gemini-embedding-001` with `output_dimensionality=768` via the `google-genai` SDK *(check the current model name in the docs)* | You already know the Gemini API, and the free tier is enough |
| LLM | Gemini Flash-class model with function calling, plus a fallback model | Same SDK; you have done model fallback before |
| Reranker | FlashRank (small ONNX cross-encoder, no PyTorch) | Runs on a small EC2 instance |
| Agent | **Hand-written tool-calling loop (no LangChain)** | Shows you understand how agents work; you can mention LangGraph as a next step |
| Frontend | React 18 + TypeScript + Vite + Tailwind + TanStack Query + React Router | Matches the Xomiro/Zenskar job descriptions |
| Streaming | Server-Sent Events (SSE) | Simpler than WebSockets for one-way token streams (you already have WebSockets in another project) |
| Tests | pytest + pytest-asyncio + **Testcontainers** (pgvector image), Vitest + React Testing Library, 1 Playwright end-to-end test | Real Postgres in the tests |
| Quality | ruff (lint + format), mypy (strict on `app/`) | Clean CI |
| Load testing | k6 | You already use it |
| Deploy | AWS: EC2 (Docker Compose) + RDS Postgres + S3 + CloudFront for the frontend; GitHub Actions → ECR → EC2 | Basic AWS (EC2/S3) is in the job descriptions |

---

## 3. Architecture

```
React (Vite) ──HTTP/SSE──▶ FastAPI ───────────────┐
                            │  /auth /documents    │
                            │  /chat (SSE)         ▼
                            │               PostgreSQL + pgvector
                            │                ├─ documents, chunks (vector + tsvector)
                            │                ├─ invoices (extracted fields)
                            │                ├─ jobs (queue, SKIP LOCKED)
                            ▼                └─ conversations, agent_runs, agent_steps
                           S3  ◀── upload       ▲
                            │                   │
                            └──▶ Worker ────────┘
                                 parse → chunk → embed → extract invoice fields
                                 (retries, backoff, visibility timeout)

Agent loop (inside /chat):
  user question → LLM (with tools) → tool calls → results → LLM → … (max 6 steps) → answer + citations
  tools: search_documents · read_chunks · query_invoices
```

---

## 4. Repository layout

```
groundwork/
├─ CLAUDE.md
├─ SPEC.md                      ← this file
├─ docker-compose.yml           ← postgres(pgvector), minio, api, worker, frontend
├─ backend/
│  ├─ pyproject.toml
│  ├─ alembic/
│  ├─ app/
│  │  ├─ main.py  config.py  db.py  logging.py
│  │  ├─ models/        ← SQLAlchemy models
│  │  ├─ schemas/       ← Pydantic request/response models
│  │  ├─ api/           ← auth.py documents.py chat.py health.py
│  │  ├─ services/      ← storage.py ingestion.py chunking.py embeddings.py
│  │  │                   retrieval.py rerank.py extraction.py
│  │  ├─ agent/         ← llm.py (provider + fake) tools.py loop.py prompts.py
│  │  └─ worker/        ← queue.py runner.py reaper.py
│  └─ tests/  unit/ integration/ conftest.py
├─ frontend/  src/ pages/ components/ api/ hooks/
├─ evals/
│  ├─ generate_corpus.py        ← synthetic PDFs + ground truth
│  ├─ build_questions.py        ← questions.jsonl from ground truth
│  ├─ run_evals.py              ← metrics → results/*.json + markdown table
│  └─ results/
├─ loadtest/ k6_search.js k6_chat.js
├─ infra/  deploy.sh  ec2-bootstrap.sh  (optional: terraform/)
├─ docs/  architecture.md  evals.md  decisions/ (short ADRs)
└─ .github/workflows/ ci.yml deploy.yml
```

---

## 5. Data model

All tables have `id UUID PK`, `created_at timestamptz`. Every tenant table has `org_id`, and **every query filters by it**.

```
orgs(id, name)
users(id, org_id FK, email UNIQUE, password_hash)

documents(id, org_id, filename, s3_key, sha256, kind ENUM(invoice,contract,other),
          status ENUM(pending,processing,ready,failed), error TEXT, page_count INT,
          UNIQUE(org_id, sha256))                         ← makes uploads idempotent

chunks(id, org_id, document_id FK ON DELETE CASCADE, ord INT, page INT,
       content TEXT, token_count INT,
       embedding vector(768),
       tsv tsvector GENERATED ALWAYS AS (to_tsvector('english', content)) STORED)
  INDEX hnsw (embedding vector_cosine_ops)
  INDEX gin (tsv)
  INDEX (org_id, document_id)

invoices(id, org_id, document_id FK, vendor TEXT, invoice_number TEXT,
         issue_date DATE, due_date DATE, currency CHAR(3),
         subtotal NUMERIC(14,2), tax NUMERIC(14,2), total NUMERIC(14,2),
         UNIQUE(org_id, vendor, invoice_number))          ← no duplicate invoices
                                                           ← NUMERIC, never float, for money

jobs(id, type TEXT, payload JSONB, status ENUM(queued,running,done,failed),
     attempts INT, max_attempts INT DEFAULT 5, run_after timestamptz,
     locked_at timestamptz, locked_by TEXT, last_error TEXT,
     idempotency_key TEXT UNIQUE)
  INDEX (status, run_after)

conversations(id, org_id, user_id, title)
messages(id, conversation_id, role ENUM(user,assistant), content TEXT, citations JSONB)
agent_runs(id, message_id, model, prompt_tokens, completion_tokens, latency_ms,
           status ENUM(ok,error,max_steps), error TEXT)
agent_steps(id, run_id, step_no, tool_name, args JSONB, result_preview TEXT, latency_ms)
```

---

## 6. Key designs (know these well, because they are the interview questions)

### 6.1 Idempotent upload
- The client uploads a file. The server computes its **sha256**. If `(org_id, sha256)` already exists, it returns the existing document with **200** instead of creating a new one with 201.
- The file goes to S3 at `orgs/{org_id}/docs/{sha256}.pdf`, so retrying the upload overwrites the same key with no orphan files.
- The document row and the `ingest` job are inserted **in one transaction**, with `idempotency_key = "ingest:{document_id}"`.

### 6.2 Job queue with SKIP LOCKED
```sql
UPDATE jobs SET status='running', locked_at=now(), locked_by=:worker, attempts=attempts+1
WHERE id = (
  SELECT id FROM jobs
  WHERE status='queued' AND run_after <= now()
  ORDER BY run_after
  FOR UPDATE SKIP LOCKED
  LIMIT 1)
RETURNING *;
```
- **On failure:** if `attempts < max_attempts`, set `status='queued'` and `run_after = now() + backoff`, where backoff is `2^attempts` seconds plus jitter. Otherwise mark the job `failed` and the document `failed` with the error.
- **Reaper:** every 30 seconds, jobs that have been `running` with `locked_at` older than 5 minutes go back to `queued`. This covers a worker crashing mid-job.
- **Crash safety for chunks:** the ingest step **deletes the document's existing chunks and inserts the new ones in one transaction**, so a re-run never duplicates chunks. This is your "0 lost, 0 duplicated" story again.

### 6.3 Ingestion pipeline (worker)
1. Download the file from S3 and parse each page with PyMuPDF.
2. **Chunk:** about 500 tokens with a 60-token overlap. Never cross a page boundary, so every chunk keeps an exact page number for citations.
3. **Embed** in batches of 50, retrying 429/5xx errors with backoff.
4. If `kind=invoice`: **extract structured fields** using LLM structured output (JSON schema → Pydantic), then **validate** them: `subtotal + tax == total` and the dates must parse. If validation fails, mark the extraction for review rather than silently storing bad numbers.
5. Set the document status to `ready`.

### 6.4 Hybrid retrieval + reranking
1. **Vector search:** top 20 by cosine distance, filtered by `org_id` (and `kind` if given).
   Use `SET LOCAL hnsw.iterative_scan = relaxed_order;` (pgvector ≥ 0.8) so filtered HNSW queries still return k results.
2. **Keyword search:** top 20 using `websearch_to_tsquery` + `ts_rank_cd`.
3. **Fuse** the two lists with **Reciprocal Rank Fusion**: `score = Σ 1/(60 + rank)`.
4. **Rerank** the fused top 20 with FlashRank and return the top 5.
5. Make every stage switchable with a flag (`mode=vector|hybrid|hybrid_rerank`) so the eval can compare them.

### 6.5 Agent loop (hand-written)
```
messages = [system_prompt, history..., user_question]
for step in range(MAX_STEPS=6):
    resp = llm.generate(messages, tools=TOOLS, timeout=30s, retries=2, fallback_model)
    if resp.tool_calls:
        for call in resp.tool_calls:
            validate args with Pydantic → run tool → record agent_step → stream "step" event
            messages.append(tool_result)        # truncated to a token budget
        continue
    answer = resp.text
    citations = validate_citations(answer, retrieved_chunk_ids)   # drop any cited id not actually retrieved
    stream "answer" + "citations" events; save agent_run; break
else:
    status = max_steps → answer "I couldn't complete this; here's what I found…"
```
**Tools** (each is a Pydantic model that is converted to a function declaration):

| Tool | Args | Does |
|---|---|---|
| `search_documents` | `query: str, kind?: invoice\|contract, top_k: int ≤ 8` | Hybrid + rerank; returns chunk ids, snippets and pages |
| `read_chunks` | `chunk_ids: list[str] (≤ 5)` | Returns full text, for when a snippet isn't enough |
| `query_invoices` | `vendor?: str, date_from?: date, date_to?: date, aggregate: sum\|count\|list, limit ≤ 50` | **Parameterised SQL only.** The LLM never writes SQL, and `org_id` is always injected by the server, not the model |

**Prompt-injection defence:** retrieved text is wrapped in `<document>` tags, and the system prompt says document content is data, not instructions. Add a test with a planted "ignore previous instructions" line in a PDF.

### 6.6 Streaming API
`POST /chat/{conversation_id}/messages` returns `text/event-stream` with events:
`step` (tool name, args, status), `token`, `citations`, `done` (run id, latency, tokens), `error`.

### 6.7 Multi-tenancy
- The JWT carries `org_id`. A FastAPI dependency injects it, and repository functions **require** it as an argument.
- **Integration test:** org B calls every endpoint and tool against org A's data and must get nothing back.

---

## 7. Synthetic data + evals (this is what makes the project stand out)

**Why synthetic:** you get **known correct answers**, so you can report real accuracy numbers instead of "it seems to work".

`evals/generate_corpus.py` (Faker + reportlab, with a fixed random seed):
- 25 vendors, about **300 invoice PDFs** with varied layouts (3 templates, some with tax and some without, mixed currencies).
- **25 contracts**, 3–6 pages each, with clauses for payment terms (net-15/30/45/60), late fee %, termination notice days, auto-renewal, liability cap and governing law. Clause positions vary so retrieval is not trivial.
- Writes `ground_truth.json`, which records each fact and **the page it is on**.

`evals/build_questions.py` → about **90 questions** in `questions.jsonl`:

| Type | Count | Example | Scored by |
|---|---|---|---|
| Contract lookup | 35 | "What is the termination notice period in the Vendor 7 contract?" | Normalised exact match + retrieval recall@5 against the gold page |
| Invoice aggregate | 35 | "Total billed by Acme between 2025-04-01 and 2025-06-30?" | Numeric exact match (Decimal) |
| Multi-hop | 20 | "Which net-45 vendor billed the most in March 2025?" | Exact match |

`evals/run_evals.py` reports:
- **Retrieval:** recall@5 and MRR@10 for each mode (`vector`, `hybrid`, `hybrid_rerank`)
- **Answer accuracy** per question type
- **Citation precision:** the share of cited chunks that contain the answer
- **p50 and p95 latency**, average tokens and estimated cost per question
- Output goes to `evals/results/{date}_{git_sha}.json`, and a markdown table is added to `docs/evals.md`

**Run the eval the first time retrieval works, then after every change.** The before/after table is your resume material.

---

## 8. Milestones (about 3 weeks, one Claude Code session each)

For each one: start in **plan mode**, paste the prompt, review the plan, let it build, **run the tests yourself**, read the diff, then commit.

### M0 — Skeleton (Day 1)
**Build:** the repo layout, `docker-compose.yml` (pgvector/pgvector:pg16, MinIO, api), FastAPI with `/health` (checks the DB and S3), Alembic initial migration, ruff + mypy + pytest configuration, and GitHub Actions CI (lint, type-check, test with a Postgres service).
**Done when:** `docker compose up` works, `curl /health` returns ok, and CI is green.
> **Prompt:** "Read SPEC.md and CLAUDE.md. Implement milestone M0 exactly as specified. Use uv, FastAPI, SQLAlchemy 2 async and Alembic. Write a pytest that hits /health against a Testcontainers pgvector database. Don't implement anything from later milestones."

### M1 — Auth + tenancy (Day 2)
**Build:** the orgs/users models, signup/login with argon2 or bcrypt, a JWT carrying `org_id`, and a `current_user` dependency.
**Done when:** the tests cover a valid/invalid login and an expired token, and a protected route rejects requests without a token.

### M2 — Upload, S3, idempotency, job queue (Days 3–4)
**Build:** `POST /documents` (multipart, PDF only, 20 MB max), sha256 dedup, S3 put, document + job in one transaction, `GET /documents`, and the queue module (enqueue/claim/complete/fail with backoff) plus the reaper.
**Done when:**
- Uploading the same file twice gives one document and one job.
- A test where two concurrent workers try to claim jobs shows each job claimed exactly once.
- A test where a job's `locked_at` is stale shows the reaper re-queues it.
> **Prompt tip:** "Write the concurrency test first: spawn 2 asyncio workers against 20 jobs and assert each job is processed exactly once."

### M3 — Ingestion worker (Days 5–6)
**Build:** the worker runner, PDF parsing, chunker, Gemini embeddings (behind an `EmbeddingProvider` interface with a deterministic `FakeEmbeddingProvider` for tests), invoice field extraction with validation, and the HNSW + GIN indexes.
**Done when:**
- Uploading a PDF eventually sets it to `ready` with chunks and embeddings.
- A test where a job is killed mid-ingest and re-run shows **no duplicate chunks**.
- An invoice whose totals don't add up is flagged.

### M4 — Synthetic corpus + eval harness + baseline retrieval (Days 7–8)
**Build:** `generate_corpus.py`, `build_questions.py`, `run_evals.py`, and **vector-only** `search_documents`.
**Done when:** you have a **baseline recall@5 / MRR number** in `docs/evals.md`. Write it down; this is your "before".

### M5 — Hybrid search + reranking (Days 9–10)
**Build:** full-text search, RRF fusion, FlashRank reranking, the `mode` flag, and the iterative-scan setting.
**Done when:** the eval table compares all three modes. Also run `EXPLAIN ANALYZE` on the search query and save the output in `docs/decisions/` as proof the indexes are used.

### M6 — Agent loop + tools + citations (Days 11–12)
**Build:** `llm.py` (Gemini + `FakeLLM` that plays back scripted tool calls), the three tools, the loop, citation validation, `agent_runs`/`agent_steps` persistence, and the prompt-injection test.
**Done when:**
- The unit tests with FakeLLM cover a multi-step run, hitting the step limit, an invalid tool argument, and a hallucinated citation being dropped.
- The eval reports **answer accuracy per question type**.

### M7 — Streaming chat API + React frontend (Days 13–15)
**Build:** the SSE endpoint, and pages for login, documents (upload with drag and drop, status badges that update by polling) and chat (streaming answer, citation chips that open the snippet and page, collapsible "Steps" panel).
**Done when:** the full flow works in the browser, there are Vitest tests for the chat stream parser and citation rendering, and 1 Playwright end-to-end test covers upload → ask → answer with a citation.

### M8 — Hardening + observability (Day 16)
**Build:**
- Structured JSON logs with a request id, and a per-org rate limit on `/chat`
- Token and cost tracking
- A `/metrics`-style admin endpoint showing p50/p95 latency, error rate and job queue depth
- k6 scripts:
  - `search` with real embeddings
  - `chat` with FakeLLM, to measure overhead without LLM latency

**Done when:** k6 numbers are recorded in `docs/evals.md`.

### M9 — AWS deployment (Days 17–19)
**Build:**
- RDS Postgres (smallest instance; enable the `vector` extension) and an S3 bucket with a least-privilege IAM role for EC2
- EC2 (t4g.small or similar) running Docker Compose with api + worker + Caddy/nginx for HTTPS
- Frontend on S3 + CloudFront
- `deploy.yml`: build → push to ECR → SSH deploy
- Secrets in SSM Parameter Store, not in `.env` files

**Done when:** a public URL works and `docs/architecture.md` has the deployed diagram.
**Before you start:** set up an **AWS Budget alarm** (for example $5), check the current Free Tier terms, and stop or delete resources you aren't using.

### M10 — Polish for recruiters (Days 20–21)
**Build:**
- README with a GIF, the architecture diagram, the eval table, and "design decisions" (link the ADRs)
- A demo login with the pre-loaded synthetic corpus
- A 2-minute demo video
- Your portfolio entry

---

## 9. CLAUDE.md (copy into the repo root)

```markdown
# Groundwork: instructions for Claude Code

Read SPEC.md before any task. Implement ONLY the milestone I name.

## Rules
- Stack is fixed (SPEC.md §2). Do not add LangChain/LlamaIndex, ORMs other than SQLAlchemy, or new infra.
- Every tenant query takes org_id explicitly. Never trust org_id from the LLM or request body.
- Money is Decimal/NUMERIC. Never float.
- The LLM never writes SQL. Tools call parameterised repository functions.
- Every external call (LLM, embeddings, S3) has a timeout and bounded retries with backoff.
- Tests: write/extend tests with each change. Integration tests use Testcontainers (pgvector/pgvector:pg16).
  Use FakeLLM / FakeEmbeddingProvider in tests, with no network calls.
- Before finishing: run `uv run ruff check . && uv run mypy app && uv run pytest` and fix failures.
- Keep functions small; add a docstring explaining *why* for any non-obvious decision.
- When you make a design choice not in SPEC.md, add a 5-line ADR in docs/decisions/.

## Commands
- Backend: `cd backend && uv run pytest`, `uv run alembic upgrade head`, `uv run python -m app.worker.runner`
- Frontend: `cd frontend && npm run dev`, `npm test`
- Evals: `uv run python evals/run_evals.py --mode hybrid_rerank`
```

---

## 10. How to work with Claude Code on this

1. **One milestone per session.** Start with "Read SPEC.md and CLAUDE.md, then plan milestone M_X." Approve the plan before it writes code.
2. **Ask for tests first** on the risky parts (queue concurrency, idempotency, tenant isolation, citation validation).
3. **Run everything yourself.** Don't accept "tests pass" without seeing it.
4. **After each milestone, ask it to quiz you.** "Ask me 5 interview questions about what we just built, then grade my answers." This is how you avoid "outsourcing understanding", which Zenskar literally screens for.
5. **Commit per milestone** with clear messages; a readable git history impresses reviewers.
6. Keep a `docs/journal.md` with bugs you hit and how you fixed them, so you have stories ready for "tell me about a hard bug".

---

## 11. Metrics to capture (fill these in as you go)

| Metric | Where it comes from | Value |
|---|---|---|
| Recall@5: vector → hybrid → hybrid+rerank | M4/M5 evals | __% → __% → __% |
| MRR@10 (same three modes) | M4/M5 evals | __ → __ → __ |
| Answer accuracy (lookup / aggregate / multi-hop) | M6 evals | __% / __% / __% |
| Citation precision | M6 evals | __% |
| p50/p95 end-to-end chat latency | M8 | 9.0 s / 9.5 s live Gemini lookups (free-tier throttled); our own overhead 122 ms / 190 ms (demo model, 10 users) |
| Search p95 under load (k6, N rps) | M8 | 24 ms warm at 20 rps; 538 ms cold (real query embedding) |
| Ingestion throughput | M8 | ~2,900 pages/min pipeline ceiling (fake AI, 1 worker); real runs are quota-bound |
| Duplicate chunks after a worker killed mid-ingest | M3 test | 0 |
| Tests / coverage | CI | 357 backend (93% line coverage) + 53 frontend, plus 1 Playwright e2e |

---

## 12. Resume entry (fill in with your measured numbers, and don't use a number you didn't measure)

**Groundwork: Document Q&A agent with citations** · GitHub | Live Demo
- Built a **tool-calling AI agent** (FastAPI, Gemini) that answers questions over invoices and contracts with **cited sources**, combining **hybrid RAG** (pgvector + Postgres full-text, RRF, reranking) with a **parameterised SQL tool** for aggregates; **__% accuracy** on a 90-question eval set.
- Raised retrieval **recall@5 from __% to __%** by adding hybrid search and cross-encoder reranking, measured with a custom evaluation harness over a synthetic corpus with known answers.
- Designed **crash-safe ingestion** on a Postgres `SKIP LOCKED` job queue with idempotent uploads, retries with backoff and a stuck-job reaper; a killed worker produced **0 duplicate chunks**.
- Deployed on **AWS (EC2, RDS, S3, CloudFront)** with GitHub Actions CI/CD; **__ tests (__% coverage)** including tenant-isolation and prompt-injection tests.
- **Tech Stack:** Python, FastAPI, PostgreSQL, pgvector, Gemini API, React, TypeScript, Docker, AWS, pytest, k6.

---

## 13. Questions you must be able to answer after building it

1. Why chunk at about 500 tokens with overlap? What happens with chunks that are too big or too small?
2. What do HNSW `m` and `ef_search` trade off? Why can filtering on `org_id` return fewer than k results, and how does the iterative scan fix it?
3. Why does hybrid search beat vector-only for queries like invoice numbers or "net-45"?
4. Explain Reciprocal Rank Fusion. Why fuse by rank instead of raw scores?
5. What does a cross-encoder reranker do that the embedding model doesn't? What is the latency cost?
6. How does `FOR UPDATE SKIP LOCKED` prevent two workers from taking the same job? What happens if a worker dies?
7. Why is the ingest step idempotent? Walk through a crash at every step.
8. How do you stop the LLM from leaking another tenant's data or running arbitrary SQL?
9. How do you detect and handle hallucinated citations?
10. How did you measure accuracy, and what are the limits of a synthetic eval set?
11. Why SSE instead of WebSockets here?
12. How would you scale this to 1M documents? (Partitioning by org, a separate vector store, async embedding backfill, caching.)
