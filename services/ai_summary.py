import json
import logging
import os
import re
from typing import Any
import anthropic
from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

TIMEOUT_SECONDS = 10.0
DEFAULT_MODEL = "claude-haiku-4-5-20251001"


class SummaryOutput(BaseModel):
    summary: str
    setting_place: str | None = None


def _clean_json_text(raw_text: str) -> str:
    """Elimina delimitadores markdown tipo ```json ... ``` si el modelo los incluye."""
    pattern = r"^```(?:json)?\s*([\s\S]*?)\s*```$"
    match = re.search(pattern, raw_text.strip())
    if match:
        return match.group(1).strip()
    return raw_text.strip()


async def generate_summary(
    title: str, category: str, wiki_text: str | None
) -> dict[str, Any] | None:
    """Genera un resumen y localización de una obra usando el SDK asíncrono de Anthropic."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        logger.warning(
            "ANTHROPIC_API_KEY no configurada. Omitiendo generación de resumen con IA."
        )
        return None

    model_name = os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)
    truncated_wiki = (wiki_text or "")[:2000]

    prompt = f"""Eres el motor de contenido de CurioMap, una app de diario y mapa cultural personal.
Analiza la siguiente obra y genera:
1. Un resumen breve y atractivo de 2 a 3 frases en español.
2. El lugar principal donde transcurre la obra (o la ciudad/lugar físico donde se encuentra, si es una obra de arte o monumento). Si no hay un lugar claro, usa null.

Obra: {title}
Categoría: {category}
Información de contexto:
{truncated_wiki}

IMPORTANTE: Responde ÚNICAMENTE con un objeto JSON válido con este formato:
{{
  "summary": "texto del resumen",
  "setting_place": "Nombre del lugar o null"
}}"""

    try:
        client = anthropic.AsyncAnthropic(
            api_key=api_key,
            timeout=TIMEOUT_SECONDS,
        )

        message = await client.messages.create(
            model=model_name,
            max_tokens=350,
            messages=[{"role": "user", "content": prompt}],
        )

        first_block = message.content[0]
        if not hasattr(first_block, "text"):
            logger.warning("Respuesta de Anthropic sin bloque de texto para '%s'", title)
            return None

        clean_text = _clean_json_text(first_block.text)
        parsed_json = json.loads(clean_text)

        # Validación estructural estricta con Pydantic
        validated = SummaryOutput.model_validate(parsed_json)
        return validated.model_dump()

    except anthropic.APIError as exc:
        logger.warning(
            "Error devuelto por la API de Anthropic para '%s': %s",
            title,
            str(exc),
        )
        return None
    except (json.JSONDecodeError, ValidationError) as exc:
        logger.warning(
            "No se pudo parsear o validar el JSON de Claude para '%s': %s",
            title,
            str(exc),
        )
        return None
    except Exception as exc:
        logger.error(
            "Error inesperado al generar resumen con Anthropic para '%s': %s",
            title,
            str(exc),
            exc_info=True,
        )
        return None