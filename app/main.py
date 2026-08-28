"""Backend: expone el RAG como una API web.

No contiene logica de RAG. Solo traduce peticion HTTP -> responder() -> JSON.

    .venv\\Scripts\\python.exe -m uvicorn app.main:app --reload
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


# --- Forma de los datos -----------------------------------------------------
# FastAPI valida las peticiones contra estas clases y genera con ellas la
# documentacion de /docs. Una peticion mal formada recibe un 422 explicativo.


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

    `def` y no `async def` a proposito: responder() bloquea esperando a
    Voyage y a Claude, y asi FastAPI la ejecuta en un hilo aparte en vez
    de congelar el servidor entero.
    """
    try:
        resultado = responder(pregunta.texto)
    except Exception as error:
        # Traduce cualquier fallo de las APIs externas a un error que el
        # navegador pueda mostrar, en vez de un 500 sin explicacion.
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
# Al final a proposito: montado en "/", si estuviera arriba taparia las
# rutas anteriores.

CARPETA_WEB = Path(__file__).resolve().parent.parent / "web"
CARPETA_WEB.mkdir(exist_ok=True)

app.mount("/", StaticFiles(directory=str(CARPETA_WEB), html=True), name="web")
