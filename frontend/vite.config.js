import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],

  // En desarrollo React vive en :5173 y la API en :8000. El proxy reenvía
  // estas rutas al backend, así el navegador cree que todo viene del mismo
  // origen y no hace falta configurar CORS en FastAPI.
  server: {
    proxy: {
      '/preguntar': 'http://127.0.0.1:8000',
      '/salud': 'http://127.0.0.1:8000',
    },
  },

  // Al compilar, dejar el resultado donde FastAPI ya sabe servir estáticos.
  build: {
    outDir: '../web',
    emptyOutDir: true,
  },
})
