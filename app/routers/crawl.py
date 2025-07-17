from fastapi import APIRouter

from app.dependencies import DBContextDep, HttpxClientDep
from app.load_data import PagesToCrawl, crawl_top_movies_and_actors

router = APIRouter(prefix="/crawl", tags=["Crawl"])


@router.post(
    "/load_movies_data",
    summary="Crawls ČSFD",
    status_code=204,
)
async def load_movies_data(
    db_context: DBContextDep,
    httpx_client: HttpxClientDep,
    pages_to_crawl: PagesToCrawl = 1,
) -> None:
    """Rebuilds our cache of the most popular movies and actors on ČSFD"""
    await crawl_top_movies_and_actors(httpx_client, db_context, pages_to_crawl)
