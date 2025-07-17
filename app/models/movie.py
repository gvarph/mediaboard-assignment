from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base
from .movie__actor import MovieActor

if TYPE_CHECKING:
    from .actor import Actor


class Movie(Base):
    """The main table for storing movie data."""

    __tablename__ = "movies"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]

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
    normalized_title: Mapped[str]

    # so we have something else to store other than the title
    rank: Mapped[int] = mapped_column()

    actors: Mapped[list["Actor"]] = relationship(
        secondary=MovieActor.__table__,
        back_populates="stared_in",
        init=False,
    )
