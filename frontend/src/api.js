/**
 * Única capa que habla con el backend.
 *
 * Las rutas son relativas a propósito: en desarrollo el proxy de Vite las
 * reenvía a :8000, y en producción FastAPI sirve la web y la API desde el
 * mismo origen. El mismo código vale para los dos casos.
 */

/**
 * Convierte la respuesta de error del backend en una frase legible.
 *
 * FastAPI devuelve dos formas distintas:
 *   502  { "detail": "Fallo al generar la respuesta: ..." }
 *   422  { "detail": [ { "msg": "...", "loc": [...] }, ... ] }
 */
async function mensajeDeError(respuesta) {
  let detalle

  try {
    const cuerpo = await respuesta.json()
    detalle = cuerpo?.detail
  } catch {
    // El cuerpo no era JSON (por ejemplo, un error del proxy).
    detalle = null
  }

  if (Array.isArray(detalle)) {
    return detalle.map((e) => e.msg).join('. ')
  }

  if (typeof detalle === 'string') {
    return detalle
  }

  return `El servidor respondió con un error ${respuesta.status}.`
}

/**
 * Envía una pregunta y devuelve la respuesta con sus fuentes.
 *
 * @param {string} texto  La pregunta del usuario.
 * @param {AbortSignal} [senal]  Permite cancelar la petición.
 * @returns {Promise<{
 *   respuesta: string,
 *   fuentes: Array<{ fuente: string, distancia: number, texto: string }>,
 *   tokens_entrada: number,
 *   tokens_salida: number,
 *   coste: number,
 * }>}
 */
export async function preguntar(texto, senal) {
  const respuesta = await fetch('/preguntar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ texto }),
    signal: senal,
  })

  // Ojo: fetch NO lanza error con un 500 o un 404. Solo falla si no hay
  // red. Hay que comprobar `ok` a mano.
  if (!respuesta.ok) {
    throw new Error(await mensajeDeError(respuesta))
  }

  return respuesta.json()
}

/**
 * Comprueba que el backend está vivo y con qué modelos está configurado.
 *
 * @param {AbortSignal} [senal]
 * @returns {Promise<{
 *   estado: string,
 *   modelo_chat: string,
 *   modelo_embeddings: string,
 * }>}
 */
export async function comprobarSalud(senal) {
  const respuesta = await fetch('/salud', { signal: senal })

  if (!respuesta.ok) {
    throw new Error(await mensajeDeError(respuesta))
  }

  return respuesta.json()
}
