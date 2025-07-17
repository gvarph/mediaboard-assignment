import asyncio
import re

import httpx
from bs4 import BeautifulSoup, Tag

from app.logger import logger

from ._query_site import load_page
from .schemas import MovieInfo

URL = "https://www.csfd.cz/zebricky/filmy/nejlepsi/?from="


id_in_url_re = re.compile(r"/film/(\d+)-")


def _parse_top_movies_page(content: bytes) -> list[MovieInfo]:
    soup = BeautifulSoup(content, "html.parser")
    movies_on_page = soup.find_all("article")
    movies: list[MovieInfo] = []
    for article in movies_on_page:
        if not isinstance(article, Tag):
            msg = "Could not parse movie info"
            raise TypeError(msg)

        rank_span = article.select_one("span.film-title-user")
        a_tag = article.select_one("a.film-title-name")
        if rank_span is None or a_tag is None:
            msg = f"Could not parse movie info, expected span and a tag, got {rank_span=} and {a_tag=}"
            raise ValueError(msg)

        rank = rank_span.get_text(strip=True).rstrip(".")
        title = a_tag.get_text(strip=True)
        url = a_tag.get("href")
        if url is None:
            msg = f"Could not parse movie info, expected href, got {url=}"
            raise ValueError(msg)

        id_match = id_in_url_re.search(str(url))
        if id_match is None:
            msg = f"Could not parse movie info, expected id in url, got {url=}"
            raise ValueError(msg)
        id_ = int(id_match.group(1))
        movie = MovieInfo(
            title=title,
            url=str(url).strip(),
            rank=int(rank),
            id=id_,
        )

        logger.trace("Parsed movie", movie=movie)
        movies.append(movie)

    return movies


async def crawl_top_movies_producer(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    page: int,
) -> list[MovieInfo]:
    """Crawl the top movies page and put the results in the queue."""
    url = URL + f"{1 if page == 1 else (page - 1) * 100}"
    with logger.contextualize(scope="crawl_top_movies", page=page):
        logger.info("Crawling top movies page")
        async with semaphore:
            content = await load_page(client, url)
        logger.debug("Finished crawling page")
        top_movies = _parse_top_movies_page(content)
        logger.trace("Parsed top movies", found_movies=len(top_movies))
        return top_movies
