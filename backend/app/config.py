from functools import lru_cache
from typing import Literal

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
    embedding_model: str = "gemini-embedding-001"
    embedding_dims: int = 768
    ai_timeout_s: float = 30
    # Minimum seconds between Gemini calls (0 = off). Keeps bulk loads inside free-tier quotas.
    embedding_min_interval_s: float = 0
    extraction_min_interval_s: float = 0
    # Free-tier generate_content quotas can be ~20 requests/day; with this off, invoices are
    # still chunked and embedded (searchable) but no invoice row is extracted.
    extraction_enabled: bool = True
    # Cost / runaway guards: a document over these limits fails instead of being embedded.
    max_pages: int = 200
    max_chunks: int = 2000
    worker_poll_s: float = 1.0
    check_timeout_s: float = 3.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
