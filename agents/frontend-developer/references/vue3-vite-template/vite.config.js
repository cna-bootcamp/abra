import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 백엔드 라우트(`app/api/routes.py`)에 등록된 모든 경로를 proxy에 추가할 것.
// 예: /chat, /health, /sessions, /mcp 등.
export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/chat':     'http://localhost:8000',
      '/health':   'http://localhost:8000',
      '/sessions': 'http://localhost:8000',
      '/mcp':      'http://localhost:8000',
    },
  },
})
