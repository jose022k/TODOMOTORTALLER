import { defineStore } from 'pinia'
import api from '../services/api'

export const useNotificationsStore = defineStore('notifications', {
  state: () => ({
    unreadCount: 0,
    notifications: [],
    knownIds: new Set(),
    pollTimer: null,
  }),
  actions: {
    async fetchUnreadCount() {
      try {
        const { data } = await api.get('/notifications/unread-count')
        this.unreadCount = data.count || 0
        if (typeof navigator.setAppBadge === 'function') {
          navigator.setAppBadge(this.unreadCount).catch(() => {})
        }
      } catch { /* silent */ }
    },
    async fetchNotifications(limit = 20) {
      try {
        const { data } = await api.get('/notifications/', { params: { limit } })
        this.notifications = Array.isArray(data) ? data : []
      } catch { /* silent */ }
    },
    // Called when a new notification arrives via WebSocket
    onNewNotification(notif) {
      if (!notif || this.knownIds.has(notif.id)) return false
      this.knownIds.add(notif.id)
      this.unreadCount++
      if (typeof navigator.setAppBadge === 'function') {
        navigator.setAppBadge(this.unreadCount).catch(() => {})
      }
      return true // was new
    },
    markOneRead(notifId) {
      this.unreadCount = Math.max(0, this.unreadCount - 1)
      const n = this.notifications.find(n => n.id === notifId)
      if (n) n.leido = true
      if (typeof navigator.setAppBadge === 'function') {
        navigator.setAppBadge(this.unreadCount).catch(() => {})
      }
    },
    markAllRead() {
      this.unreadCount = 0
      this.notifications.forEach(n => (n.leido = true))
      if (typeof navigator.setAppBadge === 'function') {
        navigator.setAppBadge(0).catch(() => {})
      }
    },
    clearAll() {
      this.notifications = []
      this.unreadCount = 0
      if (typeof navigator.setAppBadge === 'function') {
        navigator.setAppBadge(0).catch(() => {})
      }
    },
    startPolling() {
      if (this.pollTimer) return
      this.fetchUnreadCount()
      this.pollTimer = setInterval(() => this.fetchUnreadCount(), 10000)
    },
    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
    },
  },
})
