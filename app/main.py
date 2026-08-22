"""Fase 4 — Backend: exponer el RAG como una API web.

Este archivo NO contiene logica de RAG. Solo traduce:

    peticion HTTP  ->  llamada a responder()  ->  respuesta JSON

Toda la inteligencia sigue viviendo en indice.py y rag.py.

Arrancar el servidor:
    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload

Luego abrir en el navegador:
    http://127.0.0.1:8000/docs     documentacion interactiva
    http://127.0.0.1:8000/         la web (Fase 5)
"""

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from app import config
from app.rag import responder


app = FastAPI(
    title="RAG Chat — Cafe Altura",
    description="Responde preguntas usando unicamente los documentos indexados.",
    version="0.1.0",
)


# --- Forma de los datos que entran y salen ---------------------------------
# Con estas clases, FastAPI valida las peticiones automaticamente y genera
# la documentacion de /docs. Si falta un campo o llega con el tipo
# equivocado, responde un 422 explicando que esta mal.


class Pregunta(BaseModel):
    texto: str = Field(min_length=1, max_length=500)


class Fuente(BaseModel):
    fuente: str
    distancia: float
    texto: str


class Respuesta(BaseModel):
    respuesta: str
    fuentes: list[Fuente]
    tokens_entrada: int
    tokens_salida: int
    coste: float


# --- Endpoints -------------------------------------------------------------


@app.get("/salud")
def salud() -> dict:
    """Comprobacion rapida de que el servidor esta vivo y configurado."""
    return {
        "estado": "ok",
        "modelo_chat": config.MODELO_CHAT,
        "modelo_embeddings": config.MODELO_EMBEDDINGS,
    }


@app.post("/preguntar")
def preguntar(pregunta: Pregunta) -> Respuesta:
    """Responde una pregunta a partir de los documentos indexados.

    Se define con `def` y no con `async def` a proposito: responder()
    bloquea mientras espera a Voyage y a Claude. Con `def`, FastAPI la
    ejecuta en un hilo aparte y el servidor puede seguir atendiendo a
    otros clientes mientras tanto.
    """
    try:
        resultado = responder(pregunta.texto)
    except Exception as error:
        # Sin este bloque, un fallo de Voyage o de Claude tumbaria la
        # peticion con un 500 sin explicacion. Asi el navegador recibe
        # algo que se puede mostrar al usuario.
        raise HTTPException(
            status_code=502,
            detail=f"Fallo al generar la respuesta: {error}",
        ) from error

    return Respuesta(
        respuesta=resultado["respuesta"],
        fuentes=[
            Fuente(
                fuente=f["fuente"],
                distancia=f["distancia"],
                texto=f["texto"],
            )
            for f in resultado["fragmentos"]
        ],
        tokens_entrada=resultado["tokens_entrada"],
        tokens_salida=resultado["tokens_salida"],
        coste=resultado["coste"],
    )


# --- Frontend --------------------------------------------------------------
# Se monta al final para que no tape las rutas de arriba. Sirve la carpeta
# web/ tal cual: index.html en la raiz, y el resto de archivos junto a el.

CARPETA_WEB = Path(__file__).resolve().parent.parent / "web"
CARPETA_WEB.mkdir(exist_ok=True)

app.mount("/", StaticFiles(directory=str(CARPETA_WEB), html=True), name="web")
