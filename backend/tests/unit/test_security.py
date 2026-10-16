import uuid
from datetime import timedelta

import jwt
import pytest

from app.services.security import (
    TokenError,
    create_token,
    decode_token,
    hash_password,
    verify_password,
)

SECRET = "unit-test-secret-at-least-32-bytes-long"


def test_password_round_trip() -> None:
    h = hash_password("correct horse battery")
    assert h != "correct horse battery"
    assert verify_password(h, "correct horse battery")
    assert not verify_password(h, "wrong")


def test_verify_garbage_hash_is_false() -> None:
    assert not verify_password("not-a-hash", "whatever")


def test_token_round_trip() -> None:
    uid, oid = uuid.uuid4(), uuid.uuid4()
    p = decode_token(create_token(uid, oid, SECRET, timedelta(minutes=5)), SECRET)
    assert (p.user_id, p.org_id) == (uid, oid)


def test_expired_token_rejected() -> None:
    t = create_token(uuid.uuid4(), uuid.uuid4(), SECRET, timedelta(seconds=-1))
    with pytest.raises(TokenError):
        decode_token(t, SECRET)


def test_wrong_secret_rejected() -> None:
    t = create_token(uuid.uuid4(), uuid.uuid4(), SECRET, timedelta(minutes=5))
    with pytest.raises(TokenError):
        decode_token(t, "another-secret-that-is-also-32-bytes!!")


def test_alg_none_rejected() -> None:
    forged = jwt.encode({"sub": str(uuid.uuid4()), "org_id": str(uuid.uuid4())}, None, "none")
    with pytest.raises(TokenError):
        decode_token(forged, SECRET)


def test_missing_org_claim_rejected() -> None:
    t = jwt.encode({"sub": str(uuid.uuid4()), "exp": 9999999999}, SECRET, "HS256")
    with pytest.raises(TokenError):
        decode_token(t, SECRET)
