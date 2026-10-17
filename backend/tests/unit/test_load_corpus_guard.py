import sys

import pytest
from evals import load_corpus


def test_local_urls_are_recognised() -> None:
    assert load_corpus._is_local("http://localhost:8000")
    assert load_corpus._is_local("http://127.0.0.1:8000")
    assert not load_corpus._is_local("https://16-178-109-242.sslip.io")


def test_the_default_password_is_refused_against_a_real_deployment(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(load_corpus, "PASSWORD", "eval-local-only-password")
    monkeypatch.setattr(sys, "argv", ["load_corpus.py", "--api", "https://example.sslip.io"])
    with pytest.raises(SystemExit) as e:
        load_corpus.main()
    assert "strong EVAL_PASSWORD" in str(e.value)
