import axios from 'axios'

// Di production (Railway), gunakan VITE_API_URL dari environment variable.
// Di development (lokal), fallback ke proxy '/api' yang diatur di vite.config.js.
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
})

export default api
