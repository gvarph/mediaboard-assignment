from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated

from pydantic import AfterValidator
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.logger import logger
from app.models import Base


def validate_sqlite_path(path: Path) -> Path:  # noqa: D103
    if path.suffix.lower() not in {".sqlite", ".db", ".sqlite3"}:
        msg = "File extension must be .sqlite, .db or .sqlite3"
        raise ValueError(msg)
    if not path.parent.exists():
        msg = f"Directory does not exist: {path.parent}"
        raise ValueError(msg)
    return path


SQLitePath = Annotated[
    Path,
    AfterValidator(validate_sqlite_path),
]


class DBContext:  # noqa: D101
    _session_maker: async_sessionmaker[AsyncSession]

    def __init__(
        self,
        session_maker: async_sessionmaker[AsyncSession],
    ) -> None:
        self._session_maker = session_maker

    @asynccontextmanager
    async def get_session(
        self,
        *,
        auto_commit: bool = False,
        expire_on_commit: bool = False,
    ) -> AsyncGenerator[AsyncSession]:
        """
        Provides a context manager that manages the lifecycle of a database session.

        The session begins when entering the context and ends when exiting it. If 'auto_commit'
        is True, changes made during the session are committed at the end of the block,
        provided no exceptions were raised. In case of exceptions, the session's changes
        are rolled back, and the exception is re-raised. Whether changes are committed
        or rolled back, the session is always closed after the operation.

        Args:
            auto_commit: If set to True, the session commits changes at the end of
                         the block if there were no exceptions (default is False).
                         If False, the session will not automatically commit changes
                         and the caller is responsible for session.commit().
            expire_on_commit: If set to True, the session will expire on commit
                              which means you have to obtain a new session for
                              to continue working with the database (default is False).

        Yields:
            Session: A SQLAlchemy Session object, representing a workspace for your operations
                   against the database.

        Raises:
            Exception: Propagates any exceptions raised within the context of the session.
        """
        session = self._session_maker(expire_on_commit=expire_on_commit)

        try:
            yield session
            if auto_commit:
                await session.commit()
                logger.debug("Session committed")
        except Exception as e:
            logger.exception("Session rollback because of exception: %s", e)
            await session.rollback()
            raise
        finally:
            await session.close()


async def _create_tables_if_necessary(engine: AsyncEngine) -> None:
    """Create tables in the database."""
    async with engine.begin() as conn:
        logger.debug("Creating database tables")
        await conn.run_sync(Base.metadata.create_all)
        logger.debug("Database tables created")


@asynccontextmanager
async def create_db_context(
    path_to_sqlite_file: SQLitePath,
) -> AsyncGenerator[DBContext]:
    """Create a database context with a SQLite file path."""
    path = f"sqlite+aiosqlite:///{path_to_sqlite_file}"
    engine = create_async_engine(
        path,
        echo=False,  # Set True to enable SQLAlchemy logging
    )
    logger.debug("Creating database connection")
    try:
        await _create_tables_if_necessary(engine)
        yield DBContext(async_sessionmaker(engine))
    finally:
        logger.debug("Closing database connection")
        await engine.dispose()
