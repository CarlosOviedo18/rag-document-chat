import { useCallback, useRef, useState } from 'react'

import { preguntar } from '../api'

/**
 * Contador para dar una `key` estable a cada mensaje.
 *
 * Vive fuera del hook a propósito: no es estado de React, no debe provocar
 * re-render, y nunca se reinicia mientras la página siga abierta.
 */
let siguienteId = 0

/**
 * Encapsula toda la lógica de la conversación: enviar preguntas, guardar
 * los mensajes y manejar los estados de carga y error.
 *
 * Los componentes solo consumen lo que devuelve; no saben que existe fetch.
 */
export function usePreguntar() {
  const [mensajes, setMensajes] = useState([])
  const [cargando, setCargando] = useState(false)
  const [error, setError] = useState(null)

  // useRef guarda un valor entre renders SIN provocar repintado.
  // Solo lo usa el botón de reintentar para saber qué reenviar.
  const ultimaPregunta = useRef(null)

  const enviar = useCallback(
    async (texto) => {
      const limpio = texto.trim()

      // Nunca dos peticiones a la vez: el formulario también se bloquea,
      // pero conviene protegerlo aquí por si se llama desde otro sitio.
      if (!limpio || cargando) return

      ultimaPregunta.current = limpio
      setError(null)
      setCargando(true)

      // Forma de función: React nos pasa el valor actual del estado.
      // Escribir [...mensajes, nuevo] usaría la foto de cuando arrancó
      // esta función async, que puede estar desactualizada.
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
        // En el finally para que se ejecute pase lo que pase. Si solo
        // estuviera en el try, un error dejaría el indicador de carga
        // girando para siempre.
        setCargando(false)
      }
    },
    [cargando],
  )

  /**
   * Reenvía la última pregunta que falló.
   *
   * Antes quita el mensaje del usuario que quedó colgado, para que no
   * aparezca dos veces en la conversación.
   */
  const reintentar = useCallback(() => {
    const pregunta = ultimaPregunta.current
    if (!pregunta || cargando) return

    setMensajes((prev) => prev.slice(0, -1))
    enviar(pregunta)
  }, [cargando, enviar])

  return { mensajes, cargando, error, enviar, reintentar }
}
