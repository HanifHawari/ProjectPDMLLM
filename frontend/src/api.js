import axios from 'axios'

const api = axios.create({
  // Gunakan environment variable untuk URL backend, jika tidak ada gunakan '/api' (untuk lokal)
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 30000,
})

export default api
