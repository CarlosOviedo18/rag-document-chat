# RAG Chat — Chatbot sobre documentos

Aplicación web que responde preguntas usando **solo** el contenido de unos
documentos propios (en este caso, sobre café). Es un RAG:
*Retrieval-Augmented Generation*.

## Cómo funciona

```
DOCUMENTOS  ──1── trocear ──2── convertir a vectores ──► ChromaDB
                                                            │
PREGUNTA ────────── convertir a vector ──3── buscar los ────┘
                                             más parecidos
                                                  │
                                                  ▼
                            4── Claude recibe [fragmentos + pregunta]
                                y redacta la respuesta
```

El modelo nunca "aprende" los documentos. En cada pregunta se le pasan los
fragmentos relevantes como contexto.

## Puesta en marcha

```powershell
# 1. Crear el entorno virtual (ya hecho)
python -m venv .venv

# 2. Instalar dependencias
.venv\Scripts\python.exe -m pip install -r requirements.txt

# 3. Configurar claves
copy .env.example .env
#    ...y pegar dentro las claves reales

# 4. Comprobar que las APIs responden
.venv\Scripts\python.exe -m app.prueba_conexion
```

## Estructura

| Ruta | Qué contiene |
|---|---|
| `documentos/` | Los PDF y TXT de origen |
| `app/config.py` | Claves, rutas y parámetros en un solo sitio |
| `app/prueba_conexion.py` | Prueba de humo de las dos APIs |
| `app/ingesta.py` | Fase 1 — leer y trocear los documentos |
| `app/indice.py` | Fase 2 — vectorizar y guardar en ChromaDB |
| `app/rag.py` | Fase 3 — recuperar y preguntar a Claude |
| `app/main.py` | Fase 4 — la API con FastAPI |
| `web/` | Fase 5 — la interfaz de chat |

## Hoja de ruta

- [x] **Fase 0** — Entorno, estructura y prueba de conexión
- [x] **Fase 1** — Ingesta: leer los documentos y trocearlos
- [x] **Fase 2** — Índice: embeddings y ChromaDB
- [x] **Fase 3** — RAG en consola: recuperar + responder
- [x] **Fase 4** — Backend: FastAPI con endpoint `/preguntar`
- [ ] **Fase 5** — Frontend: interfaz de chat
- [ ] **Fase 6** — Mejoras: citar fuentes, historial, streaming
