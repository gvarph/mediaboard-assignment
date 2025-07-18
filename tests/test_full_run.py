from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.schemas import ActorWithMovies, MoviesAndActors, MovieWithActors


@pytest.fixture(scope="session")
# Since this is session scoped, it will keep the state including the database across all tests

def test_client() -> Generator[TestClient]:
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
def load_first_two_pages(test_client: TestClient) -> None:
    test_client.post("/crawl/load_movies_data", params={"pages_to_crawl": 2})


def test_search(test_client: TestClient) -> None:
    search_result = test_client.get("/search", params={"query": "ma"})
    assert search_result.status_code == 200

    movies_and_actors = MoviesAndActors.model_validate(search_result.json())

    assert "Matrix" in [movie.title for movie in movies_and_actors.movies]
    assert "Morgan Freeman" in [actor.name for actor in movies_and_actors.actors]


def test_get_movie(test_client: TestClient) -> None:
    movie_id = 9499

    movie_result = test_client.get(f"/movie/{movie_id}")

    assert movie_result.status_code == 200
    movie = MovieWithActors.model_validate(movie_result.json())
    assert movie.movie.title == "Matrix"
    assert len(movie.actors) > 5
    assert "Keanu Reeves" in [actor.name for actor in movie.actors]


def test_get_actor(test_client: TestClient) -> None:
    actor_id = 69

    actor_result = test_client.get(f"/actor/{actor_id}")
    assert actor_result.status_code == 200
    actor = ActorWithMovies.model_validate(actor_result.json())
    assert actor.actor.name == "Hugh Jackman"
    assert len(actor.movies) > 1
    assert "Zmizení" in [movie.title for movie in actor.movies]
