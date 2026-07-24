import axios from 'axios'

// Mengambil URL API dari environment variable Vite, dengan fallback ke '/api' untuk mode reverse proxy/development
const API_URL = import.meta.env.VITE_API_URL || '/api'

// Membuat instance Axios dengan konfigurasi dasar untuk komunikasi ke backend FastAPI
const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // Batas waktu request 30 detik untuk mengantisipasi proses LLM yang membutuhkan waktu lebih lama
})

export default api

