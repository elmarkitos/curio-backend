import asyncio
import logging
from services.wikipedia import get_wikipedia_summary

# Habilitamos logging en consola para ver advertencias o errores
logging.basicConfig(level=logging.INFO)


async def main() -> None:
    terminos = [
        ("La Alhambra", "es"),        # Caso de éxito estándar
        ("Stonehenge", "es"),          # Caso de éxito
        ("Tetsuo & Youth", "es"),      # Si no existe en español, debe saltar a 'en'
        ("asdfghjklqwertyuiop", "es"), # Término inexistente: debe devolver None sin error
    ]

    for term, lang in terminos:
        print(f"\n--- Probando: '{term}' (lang: {lang}) ---")
        resultado = await get_wikipedia_summary(term, lang=lang)

        if resultado:
            print(f"Idioma final : {resultado['lang']}")
            print(f"URL          : {resultado['url']}")
            print(f"Thumbnail    : {resultado['thumbnail']}")
            print(f"Extracto     : {resultado['extract'][:120]}...")
        else:
            print("Sin resultados (None devuelto correctamente).")


if __name__ == "__main__":
    asyncio.run(main())