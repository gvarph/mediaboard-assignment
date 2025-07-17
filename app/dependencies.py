from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import DBContext


async def db_context(
    request: Request,
) -> DBContext:
    """Provide a SQLAlchemy session for the request."""
    if not isinstance(request.app.state.db, DBContext):
        msg = f"DBContext not initialized, {type(request.app.state.db)=}"
        raise RuntimeError(msg)  # noqa: TRY004
    return request.app.state.db


DBContextDep = Annotated[DBContext, Depends(db_context)]


async def session(
    db_context: DBContextDep,
) -> AsyncGenerator[AsyncSession]:
    """Provide a SQLAlchemy session for the request."""
    async with db_context.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(session)]


async def httpx_client() -> AsyncGenerator[AsyncClient]:
    """Provide a HTTPX client for the request."""
    async with AsyncClient() as client:
        yield client


HttpxClientDep = Annotated[AsyncClient, Depends(httpx_client)]
