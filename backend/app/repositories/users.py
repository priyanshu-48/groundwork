import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Org, User


async def create_org_with_user(
    session: AsyncSession, org_name: str, email: str, password_hash: str
) -> User:
    """Org and first user in one transaction; a duplicate email raises IntegrityError."""
    org = Org(name=org_name)
    session.add(org)
    await session.flush()
    user = User(org_id=org.id, email=email, password_hash=password_hash)
    session.add(user)
    await session.flush()
    return user


async def create_user(
    session: AsyncSession, org_id: uuid.UUID, email: str, password_hash: str
) -> User:
    user = User(org_id=org_id, email=email, password_hash=password_hash)
    session.add(user)
    await session.flush()
    return user


async def get_user_by_email(session: AsyncSession, email: str) -> User | None:
    """The one deliberately un-scoped lookup: login happens before an org is known."""
    return (await session.execute(select(User).where(User.email == email))).scalar_one_or_none()
