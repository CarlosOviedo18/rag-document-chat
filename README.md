# RAG Chat — Chatbot sobre documentos propios

## Demo

https://github.com/user-attachments/assets/c7773ea7-99c4-479c-af05-d8b8ba71c611

![Demo del chat](docs/demo.gif)

> El asistente responde con los precios reales del menú, muestra de qué
> archivo salió cada dato, y admite cuando la información no está en los
> documentos.

Aplicación web que responde preguntas usando **únicamente** el contenido de
unos documentos propios. El caso de ejemplo es una cafetería costarricense:
menú, métodos de preparación, orígenes del café y preguntas frecuentes.

Es un **RAG** (*Retrieval-Augmented Generation*): el modelo no aprende los
documentos, sino que en cada pregunta se le entregan los fragmentos
relevantes como contexto.

## Cómo funciona

```
INDEXACIÓN — una vez

  documentos/*.md ──► trocear ──► Voyage ──► ChromaDB
                      400 car.    vectores   846 KB en disco
                      80 solape   de 1024

CONSULTA — en cada pregunta

  pregunta ──► Voyage ──► ChromaDB ──► Claude ──► respuesta
               vector      los 5 más    redacta   + fuentes
                           cercanos               + coste
```

La búsqueda es **semántica**: «¿qué vale un café con espuma de leche?»
encuentra «Cappuccino: ₡2.100» aunque no compartan ninguna palabra.

Y el asistente **admite cuando no sabe algo**. Si la respuesta no está en los
documentos, lo dice en vez de inventársela.

## Stack

| Capa | Tecnología |
|---|---|
| Backend | Python 3.13, FastAPI, Uvicorn, Pydantic |
| Base vectorial | ChromaDB (local, en disco) |
| Embeddings | Voyage AI — `voyage-4-lite`, 1024 dimensiones |
| Generación | Anthropic — `claude-haiku-4-5` |
| Frontend | React 19, Vite 8, Tailwind CSS 4 |

## Puesta en marcha

### 1. Backend

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt

copy .env.example .env
# ...y pegar dentro las claves reales de Anthropic y Voyage

.venv\Scripts\python.exe -m app.prueba_conexion   # comprobar que responden
.venv\Scripts\python.exe -m app.indice            # construir el índice
```

### 2. Frontend

```powershell
cd frontend
npm install
```

### 3. Arrancar (dos terminales)

```powershell
# Terminal 1 — API en :8000
.venv\Scripts\python.exe -m uvicorn app.main:app --reload

# Terminal 2 — interfaz en :5173
cd frontend
npm run dev
```

Abrir <http://localhost:5173>. La documentación interactiva de la API está en
<http://127.0.0.1:8000/docs>.

## Estructura

| Ruta | Contenido |
|---|---|
| `documentos/` | Los archivos `.md` de origen |
| `app/config.py` | Claves, rutas, modelos y parámetros del RAG |
| `app/ingesta.py` | Lee los documentos y los trocea |
| `app/indice.py` | Vectoriza con Voyage y consulta ChromaDB |
| `app/rag.py` | Recupera fragmentos y pide la respuesta a Claude |
| `app/main.py` | La API: `POST /preguntar` y `GET /salud` |
| `app/prueba_conexion.py` | Comprueba que las dos APIs responden |
| `app/prueba_trocear.py` | Comprobaciones de la función de troceado |
| `frontend/src/api.js` | Única capa que hace `fetch` |
| `frontend/src/hooks/` | `usePreguntar`: mensajes, carga y errores |
| `frontend/src/App.jsx` | La interfaz de chat |
| `chroma_db/` | Índice vectorial generado (no versionado) |
| `web/` | Frontend compilado (no versionado) |

## Comandos útiles

```powershell
# comprobar que las claves y las dos APIs funcionan
.venv\Scripts\python.exe -m app.prueba_conexion

# las 6 comprobaciones del troceado (sin coste, instantáneo)
.venv\Scripts\python.exe -m app.prueba_trocear

# ver cómo quedan los fragmentos
.venv\Scripts\python.exe -m app.ingesta

# reconstruir el índice tras cambiar los documentos
.venv\Scripts\python.exe -m app.indice --reconstruir

# probar el RAG en consola, sin frontend
.venv\Scripts\python.exe -m app.rag

# compilar el frontend a web/
cd frontend
npm run build
```

## Decisiones de diseño

**Fragmentos de 400 caracteres con 80 de solapamiento.** El valor inicial era
900, pero con un corpus de 8 500 caracteres cada consulta se llevaba el 38 %
del total. Con 400 salen 28 fragmentos del tamaño de un párrafo.

**Se recuperan 5 fragmentos, no 1.** La búsqueda vectorial acierta el tema
pero no siempre el fragmento exacto; se le dan varios candidatos al modelo y
él elige cuál responde.

**Distancia coseno.** Mide el ángulo entre vectores en vez de la distancia en
línea recta, así que un texto largo no gana por serlo.

**`upsert` en vez de `add`.** Permite reconstruir el índice sin duplicar nada.

**El endpoint es `def`, no `async def`.** La función que llama a Voyage y a
Claude bloquea, así que FastAPI la ejecuta en un hilo aparte en lugar de
congelar el servidor.

**Proxy de Vite en vez de CORS.** El mismo `fetch('/preguntar')` funciona en
desarrollo y en producción, sin variables de entorno.

**Tokens de diseño en CSS.** Ningún componente escribe un color a mano:
cambiar el tema entero es tocar un solo bloque.

## Estado

- [x] Ingesta y troceado de documentos
- [x] Índice vectorial con embeddings
- [x] Generación de respuestas con control de alucinaciones
- [x] API REST con validación automática
- [x] Interfaz de chat en React
- [ ] Citar las fuentes dentro de la respuesta
- [ ] Historial de conversación
- [ ] Respuestas en *streaming*

## Notas

- La base de datos vectorial es **local**: son archivos en `chroma_db/`, sin
  servidor ni cuenta. Pero el texto de los fragmentos sí viaja a Voyage al
  indexar, y a Anthropic al responder.
- Sin método de pago registrado, Voyage limita a **3 peticiones por minuto**.
  El código espera y reintenta, y la interfaz muestra un error con opción de
  reintentar.
- Coste aproximado: **$0,0012 por pregunta** con Haiku.
