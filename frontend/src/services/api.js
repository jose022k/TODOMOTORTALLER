import axios from 'axios'

/**
 * Resuelve la URL base de la API.
 *
 * - Desarrollo: se usa el prefijo "/api", que el servidor de desarrollo
 *   (vue.config.js) enruta hacia el backend. Así el navegador SIEMPRE habla
 *   con el mismo origen (localhost:8080 o 192.168.0.194:8080) y funciona
 *   igual desde la PC como desde cualquier otro dispositivo de la red,
 *   sin depender de la IP ni de "localhost" (que en otro equipo es él mismo).
 * - Producción: la API y el SPA comparten origen (VUE_APP_API_URL vacío).
 *
 * Si se define VUE_APP_API_URL con una URL absoluta, ésta tiene prioridad.
 */
function resolveBaseURL() {
  const configurada = process.env.VUE_APP_API_URL
  if (configurada) return configurada
  if (process.env.NODE_ENV === 'development') return '/api'
  return ''
}

const api = axios.create({
  baseURL: resolveBaseURL(),
  timeout: 60000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

let isRefreshing = false
let failedQueue = []

function processQueue(error, token) {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error)
    else resolve(token)
  })
  failedQueue = []
}

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (!error.response) {
      return Promise.reject(error)
    }
    const originalRequest = error.config
    if (error.response.status === 403) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
      if (window.location.pathname !== '/login') {
        window.location.replace('/login')
      }
      return Promise.reject(error)
    }
    if (error.response.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject })
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`
          return api(originalRequest)
        })
      }
      originalRequest._retry = true
      isRefreshing = true
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            `${api.defaults.baseURL}/auth/refresh`,
            { refresh_token: refreshToken }
          )
          localStorage.setItem('access_token', data.access_token)
          localStorage.setItem('refresh_token', data.refresh_token)

          processQueue(null, data.access_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch (e) {
          processQueue(e, null)
          localStorage.removeItem('access_token')
          localStorage.removeItem('refresh_token')
          localStorage.removeItem('user_data')
          if (window.location.pathname !== '/login') {
            window.location.replace('/login')
          }
        } finally {
          isRefreshing = false
        }
      } else {
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        localStorage.removeItem('user_data')
        if (window.location.pathname !== '/login') {
          window.location.replace('/login')
        }
      }
      isRefreshing = false
    }
    return Promise.reject(error)
  }
)

export default api
