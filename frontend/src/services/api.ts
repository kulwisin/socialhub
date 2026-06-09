import axios from 'axios'
import { authStore } from '@/lib/auth'

export const api = axios.create({
  baseURL: (process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000') + '/api/v1',
  headers: { 'Content-Type': 'application/json' },
  timeout: 60_000,
})

api.interceptors.request.use((config) => {
  const token = authStore.getState().token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authStore.getState().logout()
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    }
    const detail =
      error.response?.data?.detail ?? error.message ?? 'Something went wrong'
    return Promise.reject(new Error(detail))
  }
)
