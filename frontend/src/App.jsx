import { useState } from 'react'

import { usePreguntar } from './hooks/usePreguntar'

const SUGERENCIAS = [
  '¿Cuánto cuesta un cappuccino?',
  '¿De dónde viene el café?',
  '¿Tienen opciones sin lácteos?',
]

function Fuentes({ fuentes }) {
  const [abierto, setAbierto] = useState(false)

  return (
    <div className="mt-3 border-t border-borde pt-2">
      <button
        onClick={() => setAbierto(!abierto)}
        className="text-xs text-tenue hover:text-tinta transition-colors"
      >
        {abierto ? '− ocultar' : '+ ver'} las {fuentes.length} fuentes
      </button>

      {abierto && (
        <ul className="mt-2 space-y-2">
          {fuentes.map((f, i) => (
            <li key={i} className="text-xs text-tenue">
              <span className="font-medium text-tinta">{f.fuente}</span>
              <span className="ml-2 tabular-nums">
                {f.distancia.toFixed(3)}
              </span>
              <p className="mt-1 line-clamp-2">{f.texto}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}

function Mensaje({ mensaje }) {
  const esUsuario = mensaje.autor === 'usuario'

  return (
    <div className={esUsuario ? 'flex justify-end' : 'flex justify-start'}>
      <div
        className={
          esUsuario
            ? 'max-w-[80%] rounded-2xl rounded-br-sm bg-acento px-4 py-2.5 text-sobre-acento'
            : 'max-w-[85%] rounded-2xl rounded-bl-sm bg-superficie px-4 py-3'
        }
      >
        <p className="whitespace-pre-wrap leading-relaxed">{mensaje.texto}</p>

        {!esUsuario && mensaje.fuentes && <Fuentes fuentes={mensaje.fuentes} />}

        {!esUsuario && (
          <p className="mt-2 text-[11px] text-tenue tabular-nums">
            {mensaje.tokensEntrada + mensaje.tokensSalida} tokens · $
            {mensaje.coste.toFixed(6)}
          </p>
        )}
      </div>
    </div>
  )
}

export default function App() {
  const { mensajes, cargando, error, enviar, reintentar } = usePreguntar()
  const [texto, setTexto] = useState('')

  function alEnviar(e) {
    e.preventDefault()
    enviar(texto)
    setTexto('')
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-2xl flex-col px-5">
      <header className="border-b border-borde py-6">
        <h1 className="font-marca text-2xl">Café Altura</h1>
        <p className="mt-1 text-sm text-tenue">
          Pregunta lo que quieras. Respondo solo con lo que dicen nuestros
          documentos.
        </p>
      </header>

      <main className="flex-1 space-y-4 py-6">
        {mensajes.length === 0 && (
          <div className="space-y-2 pt-8">
            <p className="text-sm text-tenue">Prueba con:</p>
            {SUGERENCIAS.map((s) => (
              <button
                key={s}
                onClick={() => enviar(s)}
                className="block w-full rounded-xl border border-borde px-4 py-2.5 text-left text-sm hover:bg-superficie transition-colors"
              >
                {s}
              </button>
            ))}
          </div>
        )}

        {mensajes.map((m) => (
          <Mensaje key={m.id} mensaje={m} />
        ))}

        {cargando && (
          <div className="flex justify-start">
            <div className="rounded-2xl rounded-bl-sm bg-superficie px-4 py-3">
              <span className="inline-flex gap-1">
                <Punto retraso="0ms" />
                <Punto retraso="150ms" />
                <Punto retraso="300ms" />
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-borde bg-superficie px-4 py-3">
            <p className="text-sm">{error}</p>
            <button
              onClick={reintentar}
              className="mt-2 text-xs underline underline-offset-2 hover:text-tenue"
            >
              Reintentar
            </button>
          </div>
        )}
      </main>

      <form onSubmit={alEnviar} className="sticky bottom-0 bg-lienzo py-4">
        <div className="flex gap-2">
          <input
            value={texto}
            onChange={(e) => setTexto(e.target.value)}
            disabled={cargando}
            placeholder="Escribe tu pregunta…"
            maxLength={500}
            className="flex-1 rounded-xl border border-borde bg-lienzo px-4 py-3 text-sm placeholder:text-tenue disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={cargando || !texto.trim()}
            className="rounded-xl bg-acento px-5 text-sm font-medium text-sobre-acento disabled:opacity-30 transition-opacity"
          >
            Enviar
          </button>
        </div>
      </form>
    </div>
  )
}

function Punto({ retraso }) {
  return (
    <span
      className="h-1.5 w-1.5 animate-bounce rounded-full bg-tenue"
      style={{ animationDelay: retraso }}
    />
  )
}
