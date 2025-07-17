from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import DBContext


async def session(
    request: Request,
) -> AsyncGenerator[AsyncSession]:
    """Provide a SQLAlchemy session for the request."""
    if not isinstance(request.app.state.db, DBContext):
        msg = "DBContext not initialized"
        raise RuntimeError(msg)  # noqa: TRY004
    async with request.app.state.db.get_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(session)]
