import uuid
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_ph = PasswordHasher()
# Verified against when the email is unknown, so login timing does not reveal which emails exist.
DUMMY_HASH = _ph.hash("dummy-password-for-constant-time")


class TokenError(Exception):
    pass


@dataclass(frozen=True)
class Principal:
    """Who is calling. org_id comes only from a verified token, never from the request body."""

    user_id: uuid.UUID
    org_id: uuid.UUID
    demo: bool = False  # a visitor of the shared demo workspace: read-only, own conversations only


def hash_password(password: str) -> str:
    return _ph.hash(password)


def verify_password(hashed: str, password: str) -> bool:
    try:
        return _ph.verify(hashed, password)
    except (VerificationError, InvalidHashError):
        return False


def create_token(
    user_id: uuid.UUID, org_id: uuid.UUID, secret: str, ttl: timedelta, demo: bool = False
) -> str:
    claims: dict[str, object] = {
        "sub": str(user_id),
        "org_id": str(org_id),
        "exp": datetime.now(UTC) + ttl,
    }
    if demo:
        claims["demo"] = True
    return jwt.encode(claims, secret, algorithm="HS256")


def decode_token(token: str, secret: str) -> Principal:
    try:
        # algorithms is a whitelist: this is what blocks alg=none and key-confusion forgeries.
        c = jwt.decode(
            token, secret, algorithms=["HS256"], options={"require": ["exp", "sub", "org_id"]}
        )
        return Principal(uuid.UUID(c["sub"]), uuid.UUID(c["org_id"]), demo=c.get("demo") is True)
    except (jwt.PyJWTError, ValueError) as e:
        raise TokenError(str(e)) from e
