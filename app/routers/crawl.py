from fastapi import APIRouter

router = APIRouter(prefix="/crawl", tags=["Crawl"])


@router.post(
    "/crawl",
    summary="Crawls ČSFD",
    status_code=204,
)
async def crawl() -> None:
    """Rebuilds our cache of the most popular movies and actors on ČSFD"""
    raise NotImplementedError
