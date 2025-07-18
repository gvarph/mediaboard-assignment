import asyncio
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path
from pydantic import AfterValidator, Field
from sqlalchemy import bindparam, select
from sqlalchemy.orm import selectinload

from app.dependencies import SessionDep
from app.models import Actor as ActorModel
from app.models import Movie as MovieModel
from app.schemas import Actor as ActorSchema
from app.schemas import ActorWithMovies, MoviesAndActors, MovieWithActors
from app.schemas import Movie as MovieSchema
from app.utils import normalize_text

router = APIRouter(prefix="", tags=["Read"])

NormalizedSearchQuery = Annotated[
    str, Field(description="Search query", min_length=1), AfterValidator(normalize_text)
]


@router.get(
    "/search",
    summary="Search for movies and actors",
    status_code=200,
)
async def search(
    session: SessionDep,
    query: NormalizedSearchQuery,
) -> MoviesAndActors:
    """Search for movies and actors"""
    params = {"pattern": f"%{query}%"}

    actors_stmt = select(ActorModel).where(
        ActorModel.normalized_name.ilike(bindparam("pattern"))
    )
    movies_stmt = select(MovieModel).where(
        MovieModel.normalized_title.ilike(bindparam("pattern"))
    )

    actors, movies = await asyncio.gather(
        session.execute(actors_stmt, params),
        session.execute(movies_stmt, params),
    )
    actors = actors.scalars().all()
    movies = movies.scalars().all()

    return MoviesAndActors(
        movies=[MovieSchema.from_model(movie) for movie in movies],
        actors=[ActorSchema.from_model(actor) for actor in actors],
    )


@router.get(
    "/movie/{movie_id}",
    summary="Get a movie by ID",
    status_code=200,
)
async def get_movie(
    session: SessionDep, movie_id: Annotated[int, Path()]
) -> MovieWithActors:
    """Get a movie by ID"""
    stmt = (
        select(MovieModel)
        .options(selectinload(MovieModel.actors))
        .where(MovieModel.id == movie_id)
    )
    movie = await session.execute(stmt)
    movie = movie.scalar_one_or_none()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return MovieWithActors(
        movie=MovieSchema.from_model(movie),
        actors=[ActorSchema.from_model(actor) for actor in movie.actors],
    )


@router.get(
    "/actor/{actor_id}",
    summary="Get an actor by ID",
    status_code=200,
)
async def get_actor(
    session: SessionDep, actor_id: Annotated[int, Path()]
) -> ActorWithMovies:
    """Get an actor by ID"""
    stmt = (
        select(ActorModel)
        .options(selectinload(ActorModel.stared_in))
        .where(ActorModel.id == actor_id)
    )
    actor = await session.execute(stmt)
    actor = actor.scalar_one_or_none()
    if not actor:
        raise HTTPException(status_code=404, detail="Actor not found")
    return ActorWithMovies(
        actor=ActorSchema.from_model(actor),
        movies=[MovieSchema.from_model(movie) for movie in actor.stared_in],
    )
