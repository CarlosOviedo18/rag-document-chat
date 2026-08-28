import { useCallback, useRef, useState } from 'react'

import { preguntar } from '../api'

// Fuera del hook: no es estado de React y no debe provocar re-render.
let siguienteId = 0

/**
 * Encapsula la lógica de la conversación: enviar preguntas, guardar los
 * mensajes y manejar los estados de carga y error.
 *
 * Los componentes solo consumen lo que devuelve; no saben que existe fetch.
 */
export function usePreguntar() {
  const [mensajes, setMensajes] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  // useRef guarda un valor entre renders sin provocar repintado.
  const ultimaPregunta = useRef(null)

  const enviar = useCallback(
    async (texto) => {
      const limpio = texto.trim()
      if (!limpio || cargando) return

      ultimaPregunta.current = limpio
      setError(null)
      setCargando(true)

      // Forma de función: React pasa el valor actual del estado, no la
      // foto de cuando arrancó esta función async.
      setMensajes((prev) => [
        ...prev,
        { id: siguienteId++, autor: 'usuario', texto: limpio },
      ])

      try {
        const datos = await preguntar(limpio)

        setMensajes((prev) => [
          ...prev,
          {
            id: siguienteId++,
            autor: 'asistente',
            texto: datos.respuesta,
            fuentes: datos.fuentes,
            tokensEntrada: datos.tokens_entrada,
            tokensSalida: datos.tokens_salida,
            coste: datos.coste,
          },
        ])
      } catch (e) {
        setError(e.message)
      } finally {
        // En el finally: si solo estuviera en el try, un error dejaría el
        // indicador de carga girando para siempre.
        setCargando(false)
      }
    },
    [cargando],
  )

  /** Reenvía la última pregunta, quitando antes el mensaje que quedó colgado. */
  const reintentar = useCallback(() => {
    const pregunta = ultimaPregunta.current
    if (!pregunta || cargando) return

    setMensajes((prev) => prev.slice(0, -1))
    enviar(pregunta)
  }, [cargando, enviar])

  return { mensajes, cargando, error, enviar, reintentar }
}
