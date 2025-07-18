import asyncio

import httpx
from fastapi import HTTPException

from app.logger import logger
from app.scraper.movie_page import find_actors_in_movie_page

from .list_of_movies import crawl_top_movies_producer
from .schemas import ActorInfo, MovieInfo

# Heuristic value, with more, the BS4 parser was exhausting my CPU which lead to dropped requests
MAX_CONCURRENT_REQUESTS = 15

# CSFD only offers up to 10 pages (1-1000) of top movies
MAX_PAGES = 10


async def get_top_movies(
    client: httpx.AsyncClient,
    pages: int = 1,
) -> list[tuple[MovieInfo, list[ActorInfo]]]:
    """Get the top movies from ČSFD."""
    if pages > MAX_PAGES:
        msg = f"CSFD only offers up to 10 pages (1-1000) of top movies, but you requested {pages}"
        raise HTTPException(status_code=400, detail=msg)

    rate_limiter_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    movie_pages = await asyncio.gather(
        *[
            crawl_top_movies_producer(client, rate_limiter_semaphore, page)
            for page in range(1, pages + 1)
        ]
    )
    logger.info("Finished crawling list of top movies")
    movies = [movie for page in movie_pages for movie in page]
    actors = await asyncio.gather(
        *(
            find_actors_in_movie_page(client, rate_limiter_semaphore, movie)
            for movie in movies
        )
    )

    logger.info(
        "Loaded actors for all movies",
        unique_actor_count=len({actor for batch in actors for actor in batch}),
    )
    return [(movie, actors) for movie, actors in zip(movies, actors, strict=True)]
