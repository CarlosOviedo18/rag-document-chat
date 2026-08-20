"""Buscador interactivo: escribe preguntas y mira que fragmentos salen.

Todavia NO interviene Claude. Esto es solo la parte de recuperacion, para
que veas con tus propios ojos que encuentra el buscador antes de que el
modelo redacte nada.

    .venv\\Scripts\\python.exe -m app.buscar_interactivo

Escribe "salir" para terminar.

Aviso: sin tarjeta registrada, Voyage permite 3 consultas por minuto.
Si te corta, el programa espera y reintenta solo.
"""

from app import config
from app.indice import buscar


def main() -> None:
    config.verificar_claves()
    print("Escribe una pregunta sobre los documentos (o 'salir').\n")

    while True:
        pregunta = input("> ").strip()

        if pregunta.lower() in {"salir", "exit", "quit", ""}:
            print("Hasta luego.")
            break

        resultados = buscar(pregunta)

        print(f"\n{len(resultados)} fragmentos mas parecidos:\n")
        for i, r in enumerate(resultados, start=1):
            # Colapsa saltos de linea para que quepa en una linea.
            resumen = " ".join(r["texto"].split())
            print(f"{i}. distancia {r['distancia']:.3f}  ({r['fuente']})")
            print(f"   {resumen[:220]}...\n")


if __name__ == "__main__":
    main()
