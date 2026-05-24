import { defineStore } from 'pinia'
import api from '../services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    accessToken: localStorage.getItem('access_token') || null,
    refreshToken: localStorage.getItem('refresh_token') || null,
  }),
  getters: {
    isAuthenticated: (state) => !!state.accessToken,
    isAdmin: (state) => state.user?.role === 'admin',
    isMecanico: (state) => state.user?.role === 'mecanico',
    isCliente: (state) => state.user?.role === 'cliente',
  },
  actions: {
    async login(email, password) {
      const { data } = await api.post('/auth/login', { email, password })
      this.accessToken = data.access_token
      this.refreshToken = data.refresh_token
      localStorage.setItem('access_token', data.access_token)
      localStorage.setItem('refresh_token', data.refresh_token)
      await this.fetchUser()
    },
    async register(email, username, password) {
      const { data } = await api.post('/auth/register', {
        email,
        username,
        password,
      })
      return data
    },
    async fetchUser() {
      try {
        const { data } = await api.get('/auth/me')
        this.user = data
      } catch {
        this.logout()
      }
    },
    logout() {
      this.user = null
      this.accessToken = null
      this.refreshToken = null
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
    },
    async refreshAccessToken() {
      if (!this.refreshToken) return
      try {
        const { data } = await api.post('/auth/refresh', {
          refresh_token: this.refreshToken,
        })
        this.accessToken = data.access_token
        this.refreshToken = data.refresh_token
        localStorage.setItem('access_token', data.access_token)
        localStorage.setItem('refresh_token', data.refresh_token)
      } catch {
        this.logout()
      }
    },
  },
})
