from typing import Annotated

from httpx import AsyncClient
from pydantic import Field
from sqlalchemy import delete, text
from sqlalchemy.dialects.sqlite import insert

from app.db import DBContext
from app.logger import logger
from app.models import Actor, Movie
from app.models.movie__actor import MovieActor
from app.scraper import get_top_movies
from app.scraper.schemas import ActorInfo, MovieInfo
from app.utils import normalize_text

type PagesToCrawl = Annotated[
    int, Field(ge=1, le=10, description="Number of pages to crawl")
]


async def _persist_movies_and_actors(
    db_context: DBContext,
    top_movies: list[tuple[MovieInfo, list[ActorInfo]]],
) -> None:
    movies = [movie for movie, _ in top_movies]
    actors = {actor for _, actors in top_movies for actor in actors}
    logger.info("Inserting movies and actors into database")

    async with db_context.get_session() as session:
        # Clear existing data
        logger.debug("Deleting existing movie - actor associations")
        await session.execute(delete(MovieActor))
        logger.debug("Deleting existing movies")
        await session.execute(delete(Movie))
        logger.debug("Deleting existing actors")
        await session.execute(delete(Actor))

        logger.debug("Setting PRAGMAs")
        await session.execute(text("PRAGMA foreign_keys = ON"))
        await session.execute(text("PRAGMA strict = ON"))

        # Insert new data
        logger.debug("Inserting movies")
        await session.execute(
            insert(Movie).values(
                [
                    {
                        "title": movie.title,
                        "normalized_title": normalize_text(movie.title),
                        "rank": movie.rank,
                        "id": movie.id,
                    }
                    for movie in movies
                ]
            )
        )
        logger.debug("Inserting actors")
        await session.execute(
            insert(Actor).values(
                [
                    {
                        "name": actor.name,
                        "normalized_name": normalize_text(actor.name),
                        "id": actor.id,
                    }
                    for actor in actors
                ]
            )
        )
        await session.execute(
            insert(MovieActor).values(
                [
                    {"movie_id": movie.id, "actor_id": actor.id}
                    for movie, actors in top_movies
                    for actor in actors
                ]
            )
        )

        logger.debug("Finished inserting movies and actors into database, committing")
        await session.commit()
        logger.debug("Committed movies and actors into database")

    logger.info("Finished inserting movies and actors into database")


async def crawl_top_movies_and_actors(
    client: AsyncClient,
    db_context: DBContext,
    pages_to_crawl: PagesToCrawl,
) -> None:
    """Crawl top movies and actors from CSFD, and persist them into the database."""
    logger.info("Rebuilding movies cache")
    top_movies = await get_top_movies(client, pages_to_crawl)
    logger.info("Finished crawling movies")
    await _persist_movies_and_actors(db_context, top_movies)
