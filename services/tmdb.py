import logging
import os
from typing import Any
import httpx

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10.0
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


async def get_tmdb_data(title: str, category: str) -> dict[str, Any] | None:
    """Busca información de películas o series en TMDB.

    Solo actúa si category == 'movie'. Devuelve tmdbId, año, rating (1 decimal) y póster.
    """
    if category != "movie":
        return None

    api_key = os.getenv("TMDB_API_KEY")
    if not api_key:
        logger.warning(
            "TMDB_API_KEY no configurada en las variables de entorno. Omitiendo consulta TMDB."
        )
        return None

    url = f"{TMDB_BASE_URL}/search/multi"
    params = {
        "api_key": api_key,
        "query": title,
        "language": "es-ES",
        "page": 1,
    }

    try:
        timeout = httpx.Timeout(TIMEOUT_SECONDS)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()

        results = data.get("results", [])
        if not results:
            return None

        item = next(
            (result for result in results if result.get("media_type") in ("movie", "tv")),
            None,
        )
        if not item:
            return None

        raw_date = item.get("release_date") or item.get("first_air_date")
        year = raw_date[:4] if raw_date and len(raw_date) >= 4 else None

        raw_rating = item.get("vote_average")
        rating = round(float(raw_rating), 1) if raw_rating is not None else None

        poster_path = item.get("poster_path")
        image_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else None

        return {
            "tmdbId": item["id"],
            "year": year,
            "rating": rating,
            "imageUrl": image_url,
        }

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "TMDB respondió con error HTTP %s para '%s'",
            exc.response.status_code,
            title,
        )
        return None
    except httpx.RequestError as exc:
        logger.error(
            "Fallo de red o timeout conectando a TMDB para '%s': %s",
            title,
            str(exc),
        )
        return None
    except Exception as exc:
        logger.error(
            "Error inesperado al consultar TMDB para '%s': %s",
            title,
            str(exc),
            exc_info=True,
        )
        return None