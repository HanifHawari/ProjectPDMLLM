import axios from 'axios'

const api = axios.create({
  // URL akan otomatis mengambil dari .env lokal saat development, 
  // atau menggunakan URL Railway jika tidak ada di .env (saat di-deploy)
  baseURL: import.meta.env.VITE_API_URL || 'https://projectpdmllm-production.up.railway.app/api',
  timeout: 30000,
})

export default api
