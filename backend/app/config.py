from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://groundwork:groundwork@localhost:5432/groundwork"
    s3_bucket: str = "groundwork"
    s3_region: str = "us-east-1"
    # Set for MinIO / Oracle Object Storage. Leave empty for real AWS S3.
    s3_endpoint_url: str | None = None
    # Leave empty on AWS so boto3 uses the EC2 instance role (no keys on disk).
    s3_access_key: str | None = None
    s3_secret_key: str | None = None

    @field_validator("s3_endpoint_url", "s3_access_key", "s3_secret_key", mode="before")
    @classmethod
    def _empty_means_unset(cls, v: object) -> object:
        """Compose passes unset variables as empty strings; boto3 rejects an empty endpoint and
        would treat empty keys as real credentials, not fall back to the instance role."""
        return None if isinstance(v, str) and not v.strip() else v

    # No usable default: the app refuses to start without a real secret (see main.lifespan).
    jwt_secret: str = ""
    jwt_ttl_minutes: int = 60
    max_upload_bytes: int = 20 * 1024 * 1024
    job_visibility_timeout_s: float = 300
    reaper_interval_s: float = 30
    ai_provider: Literal["gemini", "fake"] = "gemini"
    gemini_api_key: str | None = None
    # Model names change; both are settings. Verify against the Gemini docs on first real run.
    gemini_model: str = "gemini-3.5-flash"
    # Comma-separated fallback chain for generation (agent + extraction), best first. Quotas are
    # per model, so listing several adds them up. Empty = just gemini_model.
    # Never used for embeddings (vectors from different models are not comparable).
    gemini_models: str = ""
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 768
    ai_timeout_s: float = 30
    # Minimum seconds between Gemini calls (0 = off). Keeps bulk loads inside free-tier quotas.
    embedding_min_interval_s: float = 0
    extraction_min_interval_s: float = 0
    agent_min_interval_s: float = 0
    # Free-tier generate_content quotas can be ~20 requests/day; with this off, invoices are
    # still chunked and embedded (searchable) but no invoice row is extracted.
    extraction_enabled: bool = True
    # Cost / runaway guards: a document over these limits fails instead of being embedded.
    max_pages: int = 200
    max_chunks: int = 2000
    worker_poll_s: float = 1.0
    # Retrieval: the default mode used by the agent's search tool (M6).
    # hybrid: best recall on the hard set at ~40 ms; hybrid_rerank costs ~2 s and was worse on
    # exact-ID queries (docs/evals.md). Revisit after reranker tuning.
    search_mode: Literal["vector", "hybrid", "hybrid_rerank"] = "hybrid"
    rerank_model: str = "ms-marco-MiniLM-L-12-v2"
    rerank_cache_dir: str = ".flashrank"
    candidate_k: int = 20
    # Agent loop limits (SPEC 6.5): bound steps, and what a tool may feed back to the model.
    agent_max_steps: int = 6
    tool_result_char_budget: int = 12000  # about 3000 tokens
    rrf_k: int = 60
    check_timeout_s: float = 3.0
    # M8 limits. In-memory and per API process (docs/decisions/0012).
    chat_rate_limit_per_min: int = 20  # per org; each chat can cost several model calls
    chat_max_concurrent: int = 3  # per org; a long run holds model quota the whole time
    search_rate_limit_per_min: int = 60  # per org; each uncached search is an embedding call
    login_rate_limit_per_min: int = 10  # per client IP (brute force)
    signup_rate_limit_per_min: int = 5  # per client IP
    query_embedding_cache_size: int = 1000
    # /admin/metrics needs this in X-Admin-Token. Empty = the route does not exist (404).
    admin_token: str = ""
    # JSON: {"model-name": [usd_per_1M_input_tokens, usd_per_1M_output_tokens]}. Empty = no cost
    # estimate (null), never a guessed price. Free tier is billed $0 whatever this says.
    model_prices: str = ""
    log_level: str = "INFO"
    # Public demo guard: when set, signup must include this code (protects the Gemini free quota).
    signup_code: str = ""


def model_chain_names(s: Settings) -> list[str]:
    names = [m.strip() for m in s.gemini_models.split(",") if m.strip()]
    return names or [s.gemini_model]


@lru_cache
def get_settings() -> Settings:
    return Settings()
