"""Comprueba que tu implementacion de trocear() es correcta.

Ejecutalo las veces que quieras mientras la escribes:

    .venv\\Scripts\\python.exe -m app.prueba_trocear

No llama a ninguna API, asi que no cuesta nada y es instantaneo.
"""

from app.ingesta import trocear


def comprobar(descripcion: str, condicion: bool, detalle: str = "") -> bool:
    marca = "[OK]  " if condicion else "[FALLA]"
    print(f"{marca} {descripcion}")
    if not condicion and detalle:
        print(f"        {detalle}")
    return condicion


def main() -> None:
    resultados = []

    # 1. Un texto corto cabe entero en un solo fragmento.
    r = trocear("Hola mundo", tamano=100, solapamiento=10)
    resultados.append(
        comprobar("Texto corto -> 1 solo fragmento", r == ["Hola mundo"], f"devolvio {r}")
    )

    # 2. El ejemplo exacto del docstring.
    r = trocear("ABCDEFGHIJKLMNOPQRSTU", tamano=10, solapamiento=3)
    esperado = ["ABCDEFGHIJ", "HIJKLMNOPQ", "OPQRSTU"]
    resultados.append(
        comprobar("Ejemplo del docstring", r == esperado, f"esperaba {esperado}\n        devolvio  {r}")
    )

    # 3. Ningun fragmento puede venir vacio.
    r = trocear("a" * 250, tamano=100, solapamiento=20)
    resultados.append(
        comprobar("Ningun fragmento vacio", all(f.strip() for f in r), f"devolvio {r}")
    )

    # 4. Ningun fragmento excede el tamano pedido.
    resultados.append(
        comprobar(
            "Ningun fragmento pasa del tamano",
            all(len(f) <= 100 for f in r),
            f"longitudes: {[len(f) for f in r]}",
        )
    )

    # 5. No se pierde texto: el primer y el ultimo caracter siguen ahi.
    texto = "".join(str(i % 10) for i in range(500))
    r = trocear(texto, tamano=120, solapamiento=30)
    resultados.append(
        comprobar(
            "No se pierde el principio ni el final",
            r[0].startswith(texto[:10]) and r[-1].endswith(texto[-10:]),
            f"primero='{r[0][:15]}...'  ultimo='...{r[-1][-15:]}'",
        )
    )

    # 6. Un solapamiento imposible debe dar un error claro, no colgarse.
    try:
        trocear("texto de prueba", tamano=10, solapamiento=10)
        ok = False
        detalle = "no lanzo ninguna excepcion (con este caso el bucle seria infinito)"
    except ValueError:
        ok, detalle = True, ""
    except NotImplementedError:
        raise
    except Exception as e:
        ok = False
        detalle = f"lanzo {type(e).__name__} en vez de ValueError"
    resultados.append(comprobar("solapamiento >= tamano lanza ValueError", ok, detalle))

    print()
    if all(resultados):
        print(f"Las {len(resultados)} comprobaciones pasan. trocear() esta lista.")
    else:
        fallos = len(resultados) - sum(resultados)
        print(f"Fallan {fallos} de {len(resultados)}. Revisa las pistas del docstring.")


if __name__ == "__main__":
    main()
