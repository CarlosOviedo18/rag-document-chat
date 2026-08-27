"""Fase 1 — Ingesta: leer los documentos y partirlos en fragmentos.

Este modulo NO habla con ninguna API. Solo manipula texto.
Es la base de todo: si los fragmentos salen mal, el chatbot respondera
mal por muy bueno que sea el modelo.

    .venv\\Scripts\\python.exe -m app.ingesta
"""

from pathlib import Path

from app import config


# Extensiones que sabemos leer.
EXTENSIONES = {".md", ".txt"}


def leer_documentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    """Lee todos los documentos de la carpeta y devuelve su texto.

    Devuelve una lista de diccionarios: {"fuente": nombre, "texto": ...}
    Guardamos el nombre del archivo porque mas adelante querremos poder
    decirle al usuario DE DONDE sale cada respuesta.
    """
    documentos = []

    for ruta in sorted(carpeta.iterdir()):
        if ruta.suffix.lower() not in EXTENSIONES:
            continue

        # encoding="utf-8" es obligatorio en Windows: sin el, los acentos
        # y el simbolo del colon salen rotos.
        texto = ruta.read_text(encoding="utf-8").strip()
        if not texto:
            print(f"  aviso: {ruta.name} esta vacio, se omite")
            continue

        documentos.append({"fuente": ruta.name, "texto": texto})

    return documentos


def trocear(
    texto: str,
    tamano: int = config.TAMANO_CHUNK,
    solapamiento: int = config.SOLAPAMIENTO_CHUNK,
) -> list[str]:
 
    if solapamiento >= tamano:
        raise ValueError(
            f"El solapamiento ({solapamiento}) debe ser menor "
            f"que el tamano ({tamano})."
        )

    fragmentos = []
    avanzar = tamano - solapamiento
    inicio = 0

    while inicio < len(texto):
        # Cortar de "inicio" hasta "inicio + tamano". Si nos pasamos del
        # final, Python devuelve lo que haya, sin dar error.
        trozo = texto[inicio:inicio + tamano].strip()

        # Un trozo puede quedar vacio al final del texto: no lo guardamos.
        if trozo:
            fragmentos.append(trozo)

        inicio += avanzar

    return fragmentos


def preparar_fragmentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    """Junta las dos piezas: lee los documentos y los trocea.

    Devuelve la lista que la Fase 2 mandara a vectorizar. Cada elemento:

        {"id": "menu.md#3", "texto": "...", "fuente": "menu.md"}

    El `id` tiene que ser unico porque ChromaDB lo usa como clave; asi,
    si reindexas, sobrescribe en vez de duplicar.
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
