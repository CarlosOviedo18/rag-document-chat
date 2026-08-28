"""Configuracion central: claves, rutas, modelos y parametros del RAG."""

from pathlib import Path

from dotenv import load_dotenv
import os

load_dotenv()

# --- Claves de API ---------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# --- Rutas -----------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DOCUMENTOS = RAIZ / "documentos"
CARPETA_CHROMA = RAIZ / "chroma_db"

# --- Modelos ---------------------------------------------------------------
# Haiku ($1 / $5 por millon) mientras se desarrolla: la misma consulta se
# lanza muchas veces. Para produccion, "claude-opus-5" (~5x precio).
MODELO_CHAT = "claude-haiku-4-5"
MODELO_EMBEDDINGS = "voyage-4-lite"

# --- Parametros del RAG ----------------------------------------------------
# Ajustado a 400 tras medir: con un corpus de ~8.500 caracteres, 900
# generaba solo 13 fragmentos y cada consulta se llevaba el 38% del total.
TAMANO_CHUNK = 400
SOLAPAMIENTO_CHUNK = 80

FRAGMENTOS_A_RECUPERAR = 5
NOMBRE_COLECCION = "cafe"


def verificar_claves() -> None:
    """Falla pronto y con un mensaje claro si falta alguna clave."""
    faltantes = [
        nombre
        for nombre, valor in (
            ("ANTHROPIC_API_KEY", ANTHROPIC_API_KEY),
            ("VOYAGE_API_KEY", VOYAGE_API_KEY),
        )
        if not valor
    ]
    if faltantes:
        raise RuntimeError(
            f"Faltan claves en el archivo .env: {', '.join(faltantes)}. "
            "Copia .env.example como .env y pega tus claves."
        )
