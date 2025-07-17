from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


class MovieActor(Base):
    """Association table between movies and actors."""

    __tablename__ = "movies__actors"

    movie_id: Mapped[int] = mapped_column(
        ForeignKey("movies.id"),
        primary_key=True,
    )
    actor_id: Mapped[int] = mapped_column(
        ForeignKey("actors.id"),
        primary_key=True,
    )
