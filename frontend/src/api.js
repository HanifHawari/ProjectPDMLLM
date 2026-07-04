import axios from 'axios'

const api = axios.create({
  // URL backend Railway di-hardcode langsung agar lebih mudah
  baseURL: 'https://projectpdmllm-production.up.railway.app/api',
  timeout: 30000,
})

export default api
