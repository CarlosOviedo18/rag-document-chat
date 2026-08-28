import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],

  // React vive en :5173 y la API en :8000. El proxy hace que el navegador
  // vea un solo origen, así que no hace falta configurar CORS en FastAPI.
  server: {
    proxy: {
      '/preguntar': 'http://127.0.0.1:8000',
      '/salud': 'http://127.0.0.1:8000',
    },
  },

  // Compila donde FastAPI ya sabe servir estáticos.
  build: {
    outDir: '../web',
    emptyOutDir: true,
  },
})
