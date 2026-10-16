from functools import lru_cache

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
    check_timeout_s: float = 3.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
