import asyncio
import logging
from dotenv import load_dotenv

# Cargamos el archivo .env si existe antes de importar los servicios
load_dotenv()

from services.tmdb import get_tmdb_data
from services.geocoding import geocode
from services.ai_summary import generate_summary

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


async def main() -> None:
    print("\n--- 1. PROBANDO TMDB ---")
    tmdb_res = await get_tmdb_data("Inception", category="movie")
    print(f"TMDB Inception: {tmdb_res}")

    tmdb_skip = await get_tmdb_data("El Quijote", category="book")
    print(f"TMDB Libro (debe ser None): {tmdb_skip}")

    print("\n--- 2. PROBANDO GEOCODING ---")
    geo1 = await geocode("La Alhambra, Granada")
    print(f"Geo 1: {geo1}")

    # Esta segunda llamada no repetirá petición a la API, entrará por caché
    geo2 = await geocode("la alhambra, granada")
    print(f"Geo 2 (desde caché): {geo2}")

    print("\n--- 3. PROBANDO RESUMEN CON ANTHROPIC ---")
    fake_wiki = (
        "Inception es una película de ciencia ficción de 2010 escrita y dirigida "
        "por Christopher Nolan. Dom Cobb es un ladrón que extrae información de los sueños..."
    )
    ai_res = await generate_summary("Inception", "movie", fake_wiki)
    print(f"Resultado IA: {ai_res}")


if __name__ == "__main__":
    asyncio.run(main())