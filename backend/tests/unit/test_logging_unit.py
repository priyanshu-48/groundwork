import json
import logging
import sys
from typing import Any

from app.logging import JsonFormatter, clean_request_id, org_id_var, request_id_var


def fmt(**kw: Any) -> dict[str, Any]:
    rec = logging.LogRecord("x", logging.INFO, "f", 1, "hello %s", ("w",), None)
    for k, v in kw.items():
        setattr(rec, k, v)
    return json.loads(JsonFormatter().format(rec))  # type: ignore[no-any-return]


def test_line_is_json_with_the_standard_fields() -> None:
    out = fmt()
    assert out["msg"] == "hello w" and out["level"] == "INFO" and out["logger"] == "x"
    assert "ts" in out
    assert "request_id" not in out  # absent, not null, outside a request


def test_context_and_extra_fields_are_included() -> None:
    t1, t2 = request_id_var.set("rid1"), org_id_var.set("org1")
    try:
        out = fmt(fields={"status": 200})
    finally:
        org_id_var.reset(t2)
        request_id_var.reset(t1)
    assert (out["request_id"], out["org_id"], out["status"]) == ("rid1", "org1", 200)


def test_exceptions_are_one_line_json() -> None:
    try:
        raise ValueError("boom")
    except ValueError:
        rec = logging.LogRecord("x", logging.ERROR, "f", 1, "bad", (), sys.exc_info())
    out = json.loads(JsonFormatter().format(rec))
    assert "ValueError: boom" in out["exc"]


def test_request_ids_are_sanitised() -> None:
    assert clean_request_id("abc-123_X") == "abc-123_X"
    for bad in (None, "", "a" * 65, "evil\nline", "has space", '{"x":1}'):
        out = clean_request_id(bad)
        assert out != bad and len(out) == 32
