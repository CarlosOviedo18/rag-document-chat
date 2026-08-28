"""Ingesta: lee los documentos de la carpeta y los parte en fragmentos.

No habla con ninguna API, solo manipula texto.

    .venv\\Scripts\\python.exe -m app.ingesta
"""

from pathlib import Path

from app import config


EXTENSIONES = {".md", ".txt"}


def leer_documentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    """Devuelve [{"fuente": nombre, "texto": contenido}, ...].

    El nombre del archivo viaja junto al texto desde aqui, para poder
    citar la fuente de cada respuesta mas adelante.
    """
    documentos = []

    for ruta in sorted(carpeta.iterdir()):
        if ruta.suffix.lower() not in EXTENSIONES:
            continue

        # encoding explicito: en Windows, sin el, los acentos salen rotos.
        texto = ruta.read_text(encoding="utf-8").strip()
        if not texto:
            continue

        documentos.append({"fuente": ruta.name, "texto": texto})

    return documentos


def trocear(
    texto: str,
    tamano: int = config.TAMANO_CHUNK,
    solapamiento: int = config.SOLAPAMIENTO_CHUNK,
) -> list[str]:
    """Parte el texto en fragmentos que se solapan entre si.

    Cada fragmento mide `tamano` pero el inicio avanza solo
    `tamano - solapamiento`, asi que cada uno repite el final del
    anterior y ninguna idea queda partida en dos trozos inservibles.
    """
    if solapamiento >= tamano:
        raise ValueError(
            f"El solapamiento ({solapamiento}) debe ser menor "
            f"que el tamano ({tamano})."
        )

    fragmentos = []
    avanzar = tamano - solapamiento
    inicio = 0

    while inicio < len(texto):
        trozo = texto[inicio:inicio + tamano].strip()
        if trozo:
            fragmentos.append(trozo)

        inicio += avanzar

    return fragmentos


def preparar_fragmentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    """Devuelve [{"id": "menu.md#3", "texto": ..., "fuente": ...}, ...].

    El id lleva delante el nombre del archivo porque la numeracion se
    reinicia en cada documento, y ChromaDB lo usa como clave unica.
    """
    fragmentos = []

    for documento in leer_documentos(carpeta):
        for numero, trozo in enumerate(trocear(documento["texto"])):
            fragmentos.append(
                {
                    "id": f"{documento['fuente']}#{numero}",
                    "texto": trozo,
                    "fuente": documento["fuente"],
                }
            )

    return fragmentos


if __name__ == "__main__":
    documentos = leer_documentos()
    print(f"Documentos leidos: {len(documentos)}")
    for doc in documentos:
        print(f"  {doc['fuente']:<32} {len(doc['texto']):>6} caracteres")

    fragmentos = preparar_fragmentos()
    print(f"\nFragmentos generados: {len(fragmentos)}")

    if fragmentos:
        print("\n--- Primer fragmento ---")
        print(f"id     : {fragmentos[0]['id']}")
        print(f"texto  : {fragmentos[0]['texto'][:200]}...")
