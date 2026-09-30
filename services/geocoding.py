import asyncio
import logging
import time
from typing import Any
import httpx

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10.0
USER_AGENT = "CurioMap/0.1 (proyecto personal)"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

# Caché en memoria: { "nombre_lugar_normalizado": resultado_dict }
_GEOCODE_CACHE: dict[str, dict[str, Any] | None] = {}

# Control de tasa para la regla de Nominatim (máx 1 petición por segundo)
_LAST_REQUEST_TIME: float = 0.0
_RATE_LIMIT_LOCK = asyncio.Lock()


async def geocode(place: str) -> dict[str, Any] | None:
    """Geocodifica un lugar usando Nominatim (OpenStreetMap).

    Incluye control de tasa (1 req/seg) y caché en memoria para no repetir consultas.
    """
    clean_place = place.strip()
    if not clean_place:
        return None

    cache_key = clean_place.lower()
    if cache_key in _GEOCODE_CACHE:
        logger.debug("Obteniendo geocodificación desde caché para '%s'", clean_place)
        return _GEOCODE_CACHE[cache_key]

    params = {
        "q": clean_place,
        "format": "jsonv2",
        "limit": 1,
    }
    headers = {"User-Agent": USER_AGENT}

    try:
        global _LAST_REQUEST_TIME
        async with _RATE_LIMIT_LOCK:
            now = time.monotonic()
            elapsed = now - _LAST_REQUEST_TIME
            if elapsed < 1.0:
                await asyncio.sleep(1.0 - elapsed)
            _LAST_REQUEST_TIME = time.monotonic()

            timeout = httpx.Timeout(TIMEOUT_SECONDS)
            async with httpx.AsyncClient(headers=headers, timeout=timeout) as client:
                response = await client.get(NOMINATIM_URL, params=params)
                response.raise_for_status()
                data = response.json()

        if not data:
            _GEOCODE_CACHE[cache_key] = None
            return None

        first = data[0]
        result = {
            "locationName": first.get("display_name", clean_place),
            "lat": float(first["lat"]),
            "lng": float(first["lon"]),
        }

        _GEOCODE_CACHE[cache_key] = result
        return result

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Nominatim respondió con error HTTP %s para '%s'",
            exc.response.status_code,
            clean_place,
        )
        return None
    except httpx.RequestError as exc:
        logger.error(
            "Fallo de conexión o timeout con Nominatim para '%s': %s",
            clean_place,
            str(exc),
        )
        return None
    except (KeyError, ValueError) as exc:
        logger.warning(
            "Formato de coordenadas no válido recibido de Nominatim para '%s': %s",
            clean_place,
            str(exc),
        )
        return None
    except Exception as exc:
        logger.error(
            "Error inesperado al geocodificar '%s': %s",
            clean_place,
            str(exc),
            exc_info=True,
        )
        return None