import asyncio
from typing import TYPE_CHECKING

import boto3
from botocore.config import Config

from app.config import Settings

if TYPE_CHECKING:
    from mypy_boto3_s3 import S3Client


def make_s3(s: Settings) -> "S3Client":
    """Bounded timeouts and retries on every S3 call (CLAUDE.md rule)."""
    return boto3.client(
        "s3",
        region_name=s.s3_region,
        endpoint_url=s.s3_endpoint_url,
        aws_access_key_id=s.s3_access_key,
        aws_secret_access_key=s.s3_secret_key,
        config=Config(
            connect_timeout=s.check_timeout_s,
            read_timeout=s.check_timeout_s * 2,
            retries={"max_attempts": 2, "mode": "standard"},
        ),
    )


async def s3_ok(client: "S3Client", bucket: str) -> bool:
    try:
        await asyncio.to_thread(client.head_bucket, Bucket=bucket)
    except Exception:
        return False
    return True


async def put_pdf(client: "S3Client", bucket: str, key: str, data: bytes) -> None:
    """Idempotent: same key, same bytes (the key embeds the sha256), so retries are harmless."""
    await asyncio.to_thread(
        client.put_object, Bucket=bucket, Key=key, Body=data, ContentType="application/pdf"
    )


async def get_bytes(client: "S3Client", bucket: str, key: str) -> bytes:
    def read() -> bytes:
        return client.get_object(Bucket=bucket, Key=key)["Body"].read()

    return await asyncio.to_thread(read)
