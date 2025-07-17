from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.movie__actor import MovieActor

from .base import Base

if TYPE_CHECKING:
    from .movie import Movie


class Actor(Base):
    """The table for storing actor data."""

    __tablename__ = "actors"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str]

    # Since this is only a simple assignment,
    #   and we will only have a few hundred movies,
    #   we can just store the normalized title and
    #   run sequential scans for search.
    #   If we wanted better performance for the search,
    #   we could would probably do one of the following:
    #   1. Not use sqlite.
    #      Most other databases have a full text search,
    #      and they would be more suitable for productio anyway.
    #   2. Use a fts5 virtual table.
    #      This would be more complex, but would turn the scans from a
    #      sequential full table scans into queries using the fts5 index.
    #   3. Only use the sqlite database for at-rest storage,
    #      and do the filtering in python
    #      (or even something like elasticsearch, but that is an overkill for this app)
    normalized_name: Mapped[str]

    stared_in: Mapped[list["Movie"]] = relationship(
        secondary=MovieActor.__table__,
        back_populates="actors",
        init=False,
    )
