import { defineStore } from 'pinia'
import api from '../services/api'

function isTokenExpired(token) {
  if (!token) return true
  try {
    const parts = token.split('.')
    if (parts.length < 2) return true
    const payloadBase64 = parts[1].replace(/-/g, '+').replace(/_/g, '/')
    const decodedJson = atob(payloadBase64)
    const decoded = JSON.parse(decodedJson)
    if (!decoded.exp) return false
    return Date.now() >= decoded.exp * 1000 - 3000
  } catch {
    return true
  }
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: JSON.parse(localStorage.getItem('user_data') || 'null'),
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
  }),
  getters: {
    isAuthenticated: (state) => {
      if (!state.accessToken) return false
      if (isTokenExpired(state.accessToken)) {
        if (!state.refreshToken || isTokenExpired(state.refreshToken)) {
          return false
        }
      }
      return true
    },
    isAdmin: (state) => state.user?.rol === 'admin',
    isMecanico: (state) => state.user?.rol === 'mecanico',
    isCliente: (state) => state.user?.rol === 'cliente',
  },
  actions: {
    async login(email, password, rol = null) {
      const payload = { email, password }
      if (rol) payload.rol = rol
      const { data } = await api.post('/auth/login', payload)
      this.accessToken = data.access_token
      this.refreshToken = data.refresh_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await this.fetchUser()
    },
    async registerCliente(payload) {
      const { data } = await api.post('/auth/register/cliente', payload)
      return data
    },
    async registerMecanico(payload) {
      const { data } = await api.post('/users/mechanics', payload)
      return data
    },
    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data
        localStorage.setItem('user_data', JSON.stringify(data))
      } catch {
        // Don't auto-logout — server might be cold-starting
      }
    },
    async logout() {
      if (this.accessToken) {
        try {
          await api.post('/auth/logout')
        } catch { /* silent */ }
      }
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_data')
    },
    async refreshAccessToken() {
      if (!this.refreshToken || isTokenExpired(this.refreshToken)) {
        await this.logout()
        return
      }
      try {
        const { data } = await api.post('/auth/refresh', {
          refresh_token: this.refreshToken,
        })
        this.accessToken = data.access_token
        this.refreshToken = data.refresh_token
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
      } catch {
        await this.logout()
      }
    },
  },
})
