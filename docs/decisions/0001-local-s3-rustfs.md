# 0001: RustFS instead of MinIO for local/test S3
- **Context:** SPEC §2 names MinIO. Its public Docker images are gone (Docker Hub repo removed, quay.io needs auth).
- **Decision:** Use `rustfs/rustfs` (S3-compatible, Apache-2.0) in docker-compose and Testcontainers. App code is unchanged: plain boto3 with `S3_ENDPOINT_URL`.
- **Why it's safe:** Only dev/test use it; prod uses real S3 (or Oracle Object Storage via the same endpoint setting).
- **Revisit:** If RustFS proves flaky, swap the image (SeaweedFS, Garage) with no code change. The tag is `latest`; pin a version once M2 relies on it.
