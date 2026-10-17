import asyncio
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user, get_session
from app.config import get_settings
from app.repositories import users
from app.schemas.auth import LoginIn, MeOut, SignupIn, TokenOut
from app.services.ratelimit import Limits, client_ip, get_limits, too_many
from app.services.security import (
    DUMMY_HASH,
    Principal,
    create_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


def _token(user_id: uuid.UUID, org_id: uuid.UUID) -> TokenOut:
    s = get_settings()
    ttl = timedelta(minutes=s.jwt_ttl_minutes)
    return TokenOut(access_token=create_token(user_id, org_id, s.jwt_secret, ttl))


@router.post("/signup", status_code=201, response_model=TokenOut)
async def signup(
    body: SignupIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
    limits: Limits = Depends(get_limits),
) -> TokenOut:
    if (wait := limits.signup.check(client_ip(request))) is not None:
        raise too_many(wait, "sign-up attempts")
    pw_hash = await asyncio.to_thread(hash_password, body.password)  # CPU-heavy: off the loop
    try:
        user = await users.create_org_with_user(session, body.org_name, body.email, pw_hash)
        await session.commit()
    except IntegrityError:
        await session.rollback()
        raise HTTPException(409, "Email already registered") from None
    return _token(user.id, user.org_id)


@router.post("/login", response_model=TokenOut)
async def login(
    body: LoginIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
    limits: Limits = Depends(get_limits),
) -> TokenOut:
    if (wait := limits.login.check(client_ip(request))) is not None:
        raise too_many(wait, "login attempts")
    user = await users.get_user_by_email(session, body.email)
    ok = await asyncio.to_thread(
        verify_password, user.password_hash if user else DUMMY_HASH, body.password
    )
    if user is None or not ok:  # same response for both, so emails cannot be enumerated
        raise HTTPException(401, "Invalid credentials")
    return _token(user.id, user.org_id)


@router.get("/me", response_model=MeOut)
async def me(p: Principal = Depends(current_user)) -> MeOut:
    return MeOut(user_id=p.user_id, org_id=p.org_id)
