import logging
from typing import Any
import httpx

# Configuramos el logger para este módulo
logger = logging.getLogger(__name__)

# Constantes del servicio
TIMEOUT_SECONDS = 10.0
USER_AGENT = "CurioMap/0.1 (proyecto personal)"
HEADERS = {"User-Agent": USER_AGENT}


async def _fetch_from_lang(
    client: httpx.AsyncClient, query: str, lang: str
) -> dict[str, Any] | None:
    """Busca un artículo en el idioma dado y extrae su resumen."""
    search_url = f"https://{lang}.wikipedia.org/w/api.php"
    search_params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "format": "json",
        "utf8": 1,
    }

    # 1. Petición de búsqueda
    response = await client.get(search_url, params=search_params)
    response.raise_for_status()
    data = response.json()

    search_results = data.get("query", {}).get("search", [])
    if not search_results:
        return None

    # Tomamos el título normalizado del primer resultado
    page_title = search_results[0]["title"]

    # 2. Petición del extracto REST
    # httpx se encarga de codificar caracteres especiales de la URL si se usa adecuadamente
    summary_url = f"https://{lang}.wikipedia.org/api/rest_v1/page/summary/{page_title}"
    summary_response = await client.get(summary_url)
    summary_response.raise_for_status()
    summary_data = summary_response.json()

    # Si devuelve tipo 'disambiguation' u otro sin extracto legible, se maneja de forma segura con .get()
    extract = summary_data.get("extract", "")
    page_url = (
        summary_data.get("content_urls", {}).get("desktop", {}).get("page", "")
    )
    thumbnail = summary_data.get("thumbnail", {}).get("source")

    return {
        "extract": extract,
        "url": page_url,
        "thumbnail": thumbnail,
        "lang": lang,
    }


async def get_wikipedia_summary(
    title: str, lang: str = "es"
) -> dict[str, Any] | None:
    """Obtiene el resumen de Wikipedia para un término dado.

    Si falla o no hay resultados en el idioma solicitado (por defecto 'es'),
    reintenta automáticamente en inglés ('en'). Nunca propaga excepciones
    de red.
    """
    timeout = httpx.Timeout(TIMEOUT_SECONDS)

    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=timeout) as client:
            # Intento 1: idioma solicitado
            result = await _fetch_from_lang(client, title, lang)
            if result:
                return result

            # Intento 2: fallback a inglés si no se pidió ya en inglés
            if lang != "en":
                logger.info(
                    "No se encontró '%s' en '%s'. Reintentando en 'en'...",
                    title,
                    lang,
                )
                return await _fetch_from_lang(client, title, "en")

            return None

    except httpx.HTTPStatusError as exc:
        logger.warning(
            "Wikipedia respondió con error HTTP %s para '%s' (idioma: %s)",
            exc.response.status_code,
            title,
            lang,
        )
        return None
    except httpx.RequestError as exc:
        logger.error(
            "Fallo de red o timeout conectando a Wikipedia con '%s': %s",
            title,
            str(exc),
        )
        return None
    except Exception as exc:
        logger.error(
            "Error inesperado al consultar Wikipedia para '%s': %s",
            title,
            str(exc),
            exc_info=True,
        )
        return None