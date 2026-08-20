"""Prueba de humo: comprueba que las dos APIs responden.

Ejecutalo antes de construir nada mas. Si esto funciona, el resto del
proyecto es solo logica; si falla, el problema es la clave o la red.

    .venv\\Scripts\\python.exe -m app.prueba_conexion
"""

import anthropic
import voyageai

from app import config


def probar_claude() -> None:
    cliente = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    respuesta = cliente.messages.create(
        model=config.MODELO_CHAT,
        max_tokens=100,
        messages=[
            {"role": "user", "content": "Responde solo con: conexion correcta."}
        ],
    )

    # response.content es una LISTA de bloques (texto, razonamiento, ...).
    # Hay que filtrar por tipo; no es un string directo.
    texto = next(b.text for b in respuesta.content if b.type == "text")

    print(f"[OK] Claude ({config.MODELO_CHAT}) responde: {texto.strip()}")
    print(f"     Tokens usados: {respuesta.usage.input_tokens} entrada / "
          f"{respuesta.usage.output_tokens} salida")


def probar_voyage() -> None:
    cliente = voyageai.Client(api_key=config.VOYAGE_API_KEY)

    resultado = cliente.embed(
        ["El café arábica se cultiva en altura."],
        model=config.MODELO_EMBEDDINGS,
        input_type="document",
    )

    vector = resultado.embeddings[0]
    print(f"[OK] Voyage ({config.MODELO_EMBEDDINGS}) responde.")
    print(f"     La frase se convirtio en un vector de {len(vector)} numeros.")
    print(f"     Primeros 5: {[round(n, 4) for n in vector[:5]]}")


if __name__ == "__main__":
    config.verificar_claves()
    probar_claude()
    probar_voyage()
    print("\nTodo listo. Puedes pasar a la Fase 1.")
