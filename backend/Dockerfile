FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv
WORKDIR /app
ENV PATH="/app/.venv/bin:$PATH"
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project
COPY . .
# Bake the reranker model into the image so the container never downloads at runtime.
RUN python -c "from flashrank import Ranker; Ranker(model_name='ms-marco-MiniLM-L-12-v2', cache_dir='/opt/flashrank')"
ENV RERANK_CACHE_DIR=/opt/flashrank
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
