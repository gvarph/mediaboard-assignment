from dataclasses import dataclass


@dataclass(slots=True)
class MovieInfo:  # noqa: D101
    title: str
    url: str
    rank: int
    id: int


@dataclass(slots=True)
class ActorInfo:  # noqa: D101
    name: str
    id: int

    def __hash__(self) -> int:  # noqa: D105
        return hash(self.id)
