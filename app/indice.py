"""Fase 2 — Indice: convertir los fragmentos en vectores y guardarlos.

Dos operaciones distintas viven aqui:

  construir_indice()  Se ejecuta UNA VEZ (o cuando cambian los documentos).
                      Lee los fragmentos, los manda a Voyage y guarda el
                      resultado en ChromaDB.

  buscar()            Se ejecuta EN CADA PREGUNTA. Convierte la pregunta
                      en un vector y pide a ChromaDB los mas parecidos.

Uso:
    .venv\\Scripts\\python.exe -m app.indice
"""

import time

import chromadb
import voyageai

from app import config
from app.ingesta import preparar_fragmentos


# Voyage no acepta miles de textos en una sola llamada. Los mandamos
# por tandas. Con 28 fragmentos sobra una, pero esto seguira funcionando
# si algun dia metes 500 documentos.
TAMANO_TANDA = 100

# Sin tarjeta registrada, Voyage limita a 3 peticiones por minuto.
# Cuando nos corta, esperamos y reintentamos en vez de reventar.
SEGUNDOS_ESPERA_LIMITE = 25
REINTENTOS = 3


def cliente_voyage() -> voyageai.Client:
    return voyageai.Client(api_key=config.VOYAGE_API_KEY)


def cliente_chroma() -> chromadb.ClientAPI:
    """Abre la base de datos vectorial en disco.

    PersistentClient guarda todo en la carpeta chroma_db/. No hay
    servidor que arrancar: son archivos, como SQLite.
    """
    return chromadb.PersistentClient(path=str(config.CARPETA_CHROMA))


def obtener_coleccion(cliente: chromadb.ClientAPI):
    """Devuelve la coleccion (el equivalente a una 'tabla').

    hnsw:space = "cosine" le dice a Chroma como medir el parecido entre
    dos vectores. La similitud del coseno mide el ANGULO entre ellos, no
    la distancia en linea recta, y es la metrica estandar para texto.
    """
    return cliente.get_or_create_collection(
        name=config.NOMBRE_COLECCION,
        metadata={"hnsw:space": "cosine"},
    )


def vectorizar(textos: list[str], tipo: str) -> list[list[float]]:
    """Convierte una lista de textos en una lista de vectores.

    El parametro `tipo` importa mas de lo que parece:

      "document"  para los fragmentos que estamos guardando
      "query"     para la pregunta del usuario

    Voyage genera vectores ligeramente distintos segun el caso, porque
    una pregunta y un fragmento que la responde no se PARECEN entre si
    (uno pregunta, el otro afirma). Avisando del rol, los acerca.
    """
    cliente = cliente_voyage()
    vectores = []

    for comienzo in range(0, len(textos), TAMANO_TANDA):
        tanda = textos[comienzo:comienzo + TAMANO_TANDA]

        for intento in range(REINTENTOS):
            try:
                respuesta = cliente.embed(
                    tanda,
                    model=config.MODELO_EMBEDDINGS,
                    input_type=tipo,
                )
                break
            except voyageai.error.RateLimitError:
                # Sin tarjeta registrada el limite es de 3 peticiones por
                # minuto. Esperamos y volvemos a intentarlo.
                if intento == REINTENTOS - 1:
                    raise
                print(
                    f"  limite de Voyage alcanzado, esperando "
                    f"{SEGUNDOS_ESPERA_LIMITE}s..."
                )
                time.sleep(SEGUNDOS_ESPERA_LIMITE)

        vectores.extend(respuesta.embeddings)

    return vectores


def construir_indice() -> int:
    """Trocea los documentos, los vectoriza y los guarda. Devuelve cuantos."""
    fragmentos = preparar_fragmentos()
    if not fragmentos:
        raise RuntimeError(
            f"No hay fragmentos. Revisa que haya documentos en {config.CARPETA_DOCUMENTOS}"
        )

    print(f"Vectorizando {len(fragmentos)} fragmentos con {config.MODELO_EMBEDDINGS}...")
    textos = [f["texto"] for f in fragmentos]
    vectores = vectorizar(textos, tipo="document")

    coleccion = obtener_coleccion(cliente_chroma())

    # upsert = insertar o reemplazar segun el id. Asi puedes reconstruir
    # el indice las veces que quieras sin duplicar nada.
    coleccion.upsert(
        ids=[f["id"] for f in fragmentos],
        documents=textos,
        embeddings=vectores,
        metadatas=[{"fuente": f["fuente"]} for f in fragmentos],
    )

    return len(fragmentos)


def buscar(pregunta: str, cuantos: int = config.FRAGMENTOS_A_RECUPERAR) -> list[dict]:
    """Devuelve los fragmentos mas parecidos a la pregunta.

    Cada resultado es un diccionario:
        {"texto": ..., "fuente": ..., "distancia": 0.31}

    La distancia va de 0 a 2: cuanto MENOR, mas parecido.
    """
    vector_pregunta = vectorizar([pregunta], tipo="query")[0]

    coleccion = obtener_coleccion(cliente_chroma())
    resultados = coleccion.query(
        query_embeddings=[vector_pregunta],
        n_results=cuantos,
    )

    # Chroma devuelve listas anidadas porque acepta varias consultas a la
    # vez. Nosotros mandamos una sola, asi que cogemos siempre el [0].
    return [
        {"texto": texto, "fuente": meta["fuente"], "distancia": distancia}
        for texto, meta, distancia in zip(
            resultados["documents"][0],
            resultados["metadatas"][0],
            resultados["distances"][0],
        )
    ]


if __name__ == "__main__":
    import sys

    config.verificar_claves()

    # Reconstruir cuesta una llamada a Voyage, asi que solo lo hacemos si
    # el indice esta vacio o si lo pides expresamente:
    #     python -m app.indice --reconstruir
    coleccion = obtener_coleccion(cliente_chroma())
    if coleccion.count() == 0 or "--reconstruir" in sys.argv:
        total = construir_indice()
        print(f"Indice construido: {total} fragmentos en {config.CARPETA_CHROMA.name}/\n")
    else:
        print(
            f"El indice ya tiene {coleccion.count()} fragmentos. "
            f"Usa --reconstruir para rehacerlo.\n"
        )

    # Preguntas que NO usan las mismas palabras que los documentos,
    # para comprobar que la busqueda va por significado.
    for pregunta in [
        "cuanto vale un cafe con espuma de leche",
        "de donde vienen los granos",
    ]:
        print(f'PREGUNTA: "{pregunta}"')
        for i, r in enumerate(buscar(pregunta, cuantos=3), start=1):
            resumen = " ".join(r["texto"].split())[:110]
            print(f"  {i}. [{r['distancia']:.3f}] ({r['fuente']}) {resumen}...")
        print()
