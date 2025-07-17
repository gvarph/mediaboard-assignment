import httpx
import tenacity
from fastapi import HTTPException, status

from app.logger import logger


@tenacity.retry(
    wait=tenacity.wait_exponential_jitter(initial=3, max=30),
    stop=tenacity.stop_after_attempt(5),
    # CSFD just cuts the connection instead of returning a 429 status code
    retry=tenacity.retry_if_exception_type(httpx.RemoteProtocolError)
    | tenacity.retry_if_exception_type(httpx.NetworkError),
    before_sleep=lambda retry_state: logger.warning(
        "Retrying request to CSFD",
        attempt=retry_state.attempt_number,
    ),
)
async def load_page(client: httpx.AsyncClient, url: str) -> bytes:
    logger.debug("Requesting page", url=url)
    response = await client.get(url, follow_redirects=True)
    logger.debug("Received response", status_code=response.status_code)
    try:
        response.raise_for_status()
    except httpx.HTTPStatusError as e:
        msg = "HTTP request to CSFD failed"
        logger.error(
            msg,
            url=url,
            status_code=e.response.status_code,
            detail=e.response.text,
            headers=e.response.headers,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=msg
        ) from e

    return response.content
