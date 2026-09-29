import axios from 'axios'

// Mengambil URL API dari environment variable Vite, dengan fallback ke '/api' untuk mode reverse proxy/development
const API_URL = import.meta.env.VITE_API_URL || '/api'

// Membuat instance Axios dengan konfigurasi dasar untuk komunikasi ke backend FastAPI
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Batas waktu request 30 detik untuk mengantisipasi proses LLM yang membutuhkan waktu lebih lama
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('fitmind_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(undefined, (error) => {
  if (error.response?.status === 401 && !error.config?.url?.endsWith('/users/login')) {
    localStorage.removeItem('fitmind_token')
    localStorage.removeItem('fitmind_user')
    localStorage.removeItem('fitmind_profile')
    window.location.assign('/login')
  }
  return Promise.reject(error)
})

export default api

