from pathlib import Path

from app import config


# Extensiones que sabemos leer.
EXTENSIONES = {".md", ".txt"}

#IMPRIME UN DICCIONARIO
def leer_documentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    documentos = []

    for ruta in sorted(carpeta.iterdir()): #reccore el for en orden con sorted

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
        trozo = texto[inicio:inicio + tamano].strip() #strip por trozo vacio
        if trozo:
            fragmentos.append(trozo)

        inicio += avanzar

    return fragmentos


def preparar_fragmentos(carpeta: Path = config.CARPETA_DOCUMENTOS) -> list[dict]:
    fragmentos = []

    for documento in leer_documentos(carpeta):
        for numero, trozo in enumerate(trocear(documento["texto"])):#como clave yvalor
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
