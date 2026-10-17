from collections.abc import AsyncIterator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.logging import org_id_var
from app.services.security import Principal, TokenError, decode_token

_bearer = HTTPBearer(auto_error=False)


async def get_session(request: Request) -> AsyncIterator[AsyncSession]:
    async with request.app.state.sessions() as session:
        yield session


def _unauthorized() -> HTTPException:
    return HTTPException(401, "Not authenticated", headers={"WWW-Authenticate": "Bearer"})


async def current_user(
    creds: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> Principal:
    """Every protected route depends on this; the org_id it returns is the only trusted one."""
    if creds is None:
        raise _unauthorized()
    try:
        principal = decode_token(creds.credentials, get_settings().jwt_secret)
    except TokenError:
        raise _unauthorized() from None
    org_id_var.set(str(principal.org_id))  # from here on every log line carries the tenant
    return principal
