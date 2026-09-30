# 🐍 CurioMap Backend

API en Python (FastAPI) para [CurioMap](https://github.com/elmarkitos/curio-map). Enriquece los marcadores del mapa cultural con información de Wikipedia, TMDB y un resumen generado por IA.

> 🚧 Proyecto personal en desarrollo, hecho para aprender.

## Qué hace

Recibe el título de una obra (libro, película, obra de arte...) y devuelve:

- Resumen de Wikipedia
- Datos de TMDB (puntuación, año, póster) para películas y series
- Un resumen corto generado con IA, pensado para un diario cultural

## Stack

- Python 3.11 o superior
- FastAPI + Uvicorn
- httpx (llamadas a APIs externas)
- Anthropic SDK (resúmenes con IA)
- python-dotenv (variables de entorno)

## Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/health` | Comprueba que el servidor está vivo |
| GET | `/enrich?title=...&category=...` | Devuelve resumen, puntuación, año y póster |

Documentación interactiva automática en `http://localhost:8000/docs`.

## Estado

- [ ] Servidor base y `/health`
- [ ] CORS para el frontend
- [ ] Servicio de Wikipedia
- [ ] Servicio de TMDB
- [ ] Resumen con IA
- [ ] Endpoint `/enrich`
- [ ] Despliegue (Railway / Render)

## Cómo ejecutarlo

Requisitos: Python 3.11+ y Git.

```bash
git clone https://github.com/elmarkitos/curio-backend.git
cd curio-backend

# Entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Mac / Linux

pip install -r requirements.txt

# Variables de entorno
copy .env.example .env       # Windows
# cp .env.example .env       # Mac / Linux
# Edita .env y rellena tus propias claves

uvicorn main:app --reload
```

## Variables de entorno

Copia `.env.example` a `.env` y rellena:

| Variable | Dónde conseguirla |
|---|---|
| `TMDB_API_KEY` | https://www.themoviedb.org/settings/api |
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `ALLOWED_ORIGINS` | URLs del frontend permitidas, separadas por comas |

El archivo `.env` está en `.gitignore`. Nunca subas claves al repositorio.

## Estructura prevista

```
curio-backend/
├── main.py              # app FastAPI y endpoints
├── services/
│   ├── wikipedia.py
│   ├── tmdb.py
│   └── ai_summary.py
├── requirements.txt
├── .env.example
└── README.md
```

## Licencia

MIT