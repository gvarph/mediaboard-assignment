from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from pydantic import RootModel

from app.db import SQLitePath, create_db_context
from app.logger import logger
from app.routers.crawl import router as crawl_router

SQLITE_FILE_PATH = RootModel[SQLitePath].model_validate("./crawled.db").root


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Performs tasks that should be done at the start and end of the application's lifespan."""
    logger.debug("Creating database context")
    async with create_db_context(SQLITE_FILE_PATH) as db:
        app.state.db = db
        yield


app = FastAPI(lifespan=lifespan)

app.include_router(crawl_router)
