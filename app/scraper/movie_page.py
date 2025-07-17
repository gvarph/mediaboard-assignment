import asyncio
import re

import httpx
from bs4 import BeautifulSoup, Tag

from app.logger import logger

from ._query_site import load_page
from .schemas import ActorInfo, MovieInfo

BASE_URL = "https://www.csfd.cz"


actor_re = re.compile(r"/tvurce/(\d+)-")


def _extract_actors_from_page(content: bytes) -> list[ActorInfo]:
    soup = BeautifulSoup(content, "html.parser")
    creators_div = soup.select_one("div.creators")

    if not creators_div:
        msg = "Could not find creators div"
        raise ValueError(msg)

    # Inside that, find a div that contains <h4>Hrají:</h4>
    for div in creators_div.find_all("div", recursive=False):
        if not isinstance(div, Tag):
            continue
        h4 = div.find("h4")
        if h4 and h4.get_text(strip=True) == "Hrají:":
            hraji_div = div
            break
    else:
        # This for example happens on animated movies such as https://www.csfd.cz/film/350930-krtek/prehled/
        logger.warning("Could not find hrají div, assuming no actors")
        return []

    results: list[ActorInfo] = []
    for a in hraji_div.find_all("a"):
        logger.trace("Found actor link", a=a)
        if not isinstance(a, Tag):
            msg = "Could not found a invalid actor link"
            raise ValueError(msg)  # noqa: TRY004

        link_text = a.get_text(strip=True)
        href = str(a["href"])
        logger.trace("parsing actor link", parsed_link_text=link_text, parsed_href=href)

        if href == "#":  # Used for the "More" link that expands the list of actors
            continue

        id_match = actor_re.match(href)
        logger.trace("Found actor id match", id_match=id_match)
        if not id_match or not id_match.group(1):
            msg = f"Could not find actor id in link, {href=}"
            raise ValueError(msg)
        id_ = int(id_match.group(1))
        logger.trace("Parsed actor id", id=id_)
        results.append(
            ActorInfo(
                name=link_text,
                id=id_,
            )
        )

    return results


async def find_actors_in_movie_page(
    client: httpx.AsyncClient,
    semaphore: asyncio.Semaphore,
    movie: MovieInfo,
) -> list[ActorInfo]:
    """Consumes MovieInfo from input_queue, fetches their actors, returns the enriched MovieInfo."""
    with logger.contextualize(scope="crawl_actors", movie_url=movie.url):
        async with semaphore:
            logger.trace("Crawling actors")
            content = await load_page(client, BASE_URL + movie.url)
            # Part of the semaphore so we don't overload the client
            # which can cause the requests to timeout
            # because BS4 is not exactly fast.
            actors = _extract_actors_from_page(content)
        logger.debug("Parsed actors", count=len(actors))
        return actors
