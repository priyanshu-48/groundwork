import pytest

from app.config import Settings
from app.services.storage import make_s3


def settings(**env: str) -> Settings:
    return Settings(_env_file=None, **env)  # type: ignore[arg-type]


def test_empty_s3_values_mean_unset(monkeypatch: pytest.MonkeyPatch) -> None:
    """docker-compose passes unset variables as empty strings. On AWS the endpoint and keys must
    stay unset so boto3 uses the instance role; an empty endpoint made the API crash at startup."""
    for k in ("S3_ENDPOINT_URL", "S3_ACCESS_KEY", "S3_SECRET_KEY"):
        monkeypatch.setenv(k, "")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert (s.s3_endpoint_url, s.s3_access_key, s.s3_secret_key) == (None, None, None)
    client = make_s3(s)  # must not raise
    assert "amazonaws.com" in client.meta.endpoint_url


def test_real_s3_values_are_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("S3_ENDPOINT_URL", "http://s3:9000")
    monkeypatch.setenv("S3_ACCESS_KEY", "k")
    s = Settings(_env_file=None)  # type: ignore[call-arg]
    assert s.s3_endpoint_url == "http://s3:9000" and s.s3_access_key == "k"
