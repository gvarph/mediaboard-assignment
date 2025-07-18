from typing import Self

from pydantic import BaseModel

from app.models import Actor as ActorModel
from app.models import Movie as MovieModel


class Movie(BaseModel):  # noqa: D101
    title: str
    rank: int
    id: int

    @classmethod
    def from_model(cls, model: MovieModel) -> Self:  # noqa: D102
        return cls(
            title=model.title,
            rank=model.rank,
            id=model.id,
        )


class Actor(BaseModel):  # noqa: D101
    name: str
    id: int

    @classmethod
    def from_model(cls, model: ActorModel) -> Self:  # noqa: D102
        return cls(
            name=model.name,
            id=model.id,
        )


class ActorWithMovies(BaseModel):  # noqa: D101
    actor: Actor
    movies: list[Movie]


class MovieWithActors(BaseModel):  # noqa: D101
    movie: Movie
    actors: list[Actor]


class MoviesAndActors(BaseModel):  # noqa: D101
    movies: list[Movie]
    actors: list[Actor]
