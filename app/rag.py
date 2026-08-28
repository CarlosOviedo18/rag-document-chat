
import anthropic

from app import config
from app.indice import buscar


# Precio por millon de tokens (entrada, salida) en dolares.
# Solo sirve para mostrar el coste en pantalla.
PRECIOS = {
    "claude-haiku-4-5": (1.0, 5.0),
    "claude-sonnet-5": (3.0, 15.0),
    "claude-opus-5": (5.0, 25.0),
}


INSTRUCCIONES = """Eres el asistente de Cafe Altura, una cafeteria costarricense.

Respondes preguntas de clientes usando UNICAMENTE la informacion de los
fragmentos que se te entregan.

Reglas:
- Si la respuesta no esta en los fragmentos, di que no tienes ese dato y
  sugiere preguntarlo en el local. NUNCA te lo inventes ni completes con
  conocimiento general sobre cafe.
- No menciones "fragmentos", "contexto" ni "documentos". El cliente no sabe
  que existen: responde como si simplemente lo supieras.
- Tono neutro y directo. Informa sin adornos ni formulas de cortesia.
- Se breve: dos o tres frases, salvo que pidan detalle.
- Los precios van en colones, con el simbolo cuando aparezca en la fuente.
- Responde en el idioma en que te pregunten."""


def construir_contexto(fragmentos: list[dict]) -> str:

    partes = []

    for numero, fragmento in enumerate(fragmentos, start=1):
        partes.append(
            f"[Fragmento {numero} — fuente: {fragmento['fuente']}]\n"
            f"{fragmento['texto']}"
        )

    return "\n\n".join(partes)


def calcular_coste(modelo: str, entrada: int, salida: int) -> float:
    """Coste aproximado de una consulta, en dolares."""
    precio_entrada, precio_salida = PRECIOS.get(modelo, (0.0, 0.0))
    return entrada / 1_000_000 * precio_entrada + salida / 1_000_000 * precio_salida


def responder(pregunta: str) -> dict:

    fragmentos = buscar(pregunta)
    contexto = construir_contexto(fragmentos)

    cliente = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)

    # "system" son las reglas: no cambian nunca.
    # "messages" son los datos de esta consulta concreta.
    respuesta = cliente.messages.create(
        model=config.MODELO_CHAT,
        max_tokens=1000,
        system=INSTRUCCIONES,
        messages=[
            {
                "role": "user",
                "content": (
                    f"{contexto}\n\n"
                    f"---\n\n"
                    f"Pregunta del cliente: {pregunta}"
                ),
            }
        ],
    )

    # respuesta.content es una LISTA de bloques. Cogemos el primero de texto.
    texto = next(b.text for b in respuesta.content if b.type == "text")

    return {
        "respuesta": texto.strip(),
        "fragmentos": fragmentos,
        "tokens_entrada": respuesta.usage.input_tokens,
        "tokens_salida": respuesta.usage.output_tokens,
        "coste": calcular_coste(
            config.MODELO_CHAT,
            respuesta.usage.input_tokens,
            respuesta.usage.output_tokens,
        ),
    }


def mostrar(resultado: dict) -> None:
    print(f"\n{resultado['respuesta']}\n")

    print("  " + "-" * 66)
    print("  FRAGMENTOS RECUPERADOS")
    for numero, fragmento in enumerate(resultado["fragmentos"], start=1):
        resumen = " ".join(fragmento["texto"].split())[:90]
        print(
            f"  {numero}. [{fragmento['distancia']:.3f}] "
            f"({fragmento['fuente']}) {resumen}..."
        )

    print(
        f"  {resultado['tokens_entrada']} tokens entrada / "
        f"{resultado['tokens_salida']} salida  ·  "
        f"${resultado['coste']:.6f}  ·  {config.MODELO_CHAT}"
    )
    print("  " + "-" * 66)


if __name__ == "__main__":
    config.verificar_claves()

    print(f"Asistente de Cafe Altura ({config.MODELO_CHAT})")
    print("Escribe una pregunta, o 'salir' para terminar.\n")

    gasto_total = 0.0

    while True:
        pregunta = input("> ").strip()

        if pregunta.lower() in {"salir", "exit", "quit", ""}:
            print(f"\nGasto de esta sesion: ${gasto_total:.6f}")
            break

        resultado = responder(pregunta)
        gasto_total += resultado["coste"]
        mostrar(resultado)
