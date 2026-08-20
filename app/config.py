"""Configuracion central del proyecto.

Todo lo que sea una constante o una clave vive aqui, para no tener
numeros magicos repartidos por el codigo.
"""

from pathlib import Path

from dotenv import load_dotenv
import os

# Carga las variables del archivo .env a las variables de entorno del proceso.
load_dotenv()

# --- Claves de API ---------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
VOYAGE_API_KEY = os.getenv("VOYAGE_API_KEY")

# --- Rutas -----------------------------------------------------------------
RAIZ = Path(__file__).resolve().parent.parent
CARPETA_DOCUMENTOS = RAIZ / "documentos"
CARPETA_CHROMA = RAIZ / "chroma_db"

# --- Modelos ---------------------------------------------------------------
# Haiku es el modelo mas barato ($1 / $5 por millon de tokens): ideal
# mientras desarrollamos, porque lanzaremos la misma consulta muchas veces.
# Para la version final, cambiar a "claude-opus-5" (mejor calidad, ~5x precio).
MODELO_CHAT = "claude-haiku-4-5"

# voyage-4-lite: generacion mas reciente, multilingue, vectores de 1024
# dimensiones. Comprobado que la clave tiene acceso (ver Fase 0).
MODELO_EMBEDDINGS = "voyage-4-lite"

# --- Parametros del RAG ----------------------------------------------------
# Tamano de cada fragmento de texto, en caracteres.
# Muy pequeno = pierdes contexto. Muy grande = el fragmento trae mucho ruido.
# Ajustado a 400 tras medir: con un corpus de ~8.500 caracteres, 900
# generaba solo 13 fragmentos y cada consulta se llevaba el 38% de todo.
# Con 400 salen 28 fragmentos del tamano de un parrafo.
TAMANO_CHUNK = 400

# Cuantos caracteres comparte un fragmento con el siguiente.
# Evita cortar una idea justo por la mitad.
SOLAPAMIENTO_CHUNK = 80

# Cuantos fragmentos recuperamos para responder una pregunta.
FRAGMENTOS_A_RECUPERAR = 5

# Nombre de la coleccion dentro de ChromaDB.
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
