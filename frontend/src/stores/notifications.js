import { defineStore } from 'pinia'
import api from '../services/api'

function updateNativeAppBadge(count) {
  try {
    if ('setAppBadge' in navigator) {
      if (count > 0) {
        navigator.setAppBadge(count).catch(() => {})
      } else if ('clearAppBadge' in navigator) {
        navigator.clearAppBadge().catch(() => {})
      } else {
        navigator.setAppBadge(0).catch(() => {})
      }
    }
  } catch { /* unsupported */ }
}

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
        updateNativeAppBadge(this.unreadCount)
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
      if (!notif) return false
      const idKey = notif.id ? String(notif.id) : ('notif-temp-' + Date.now() + '-' + Math.random())
      if (this.knownIds.has(idKey)) return false
      this.knownIds.add(idKey)
      this.unreadCount++
      updateNativeAppBadge(this.unreadCount)
      return true // was new
    },
    markOneRead(notifId) {
      this.unreadCount = Math.max(0, this.unreadCount - 1)
      const n = this.notifications.find(n => n.id === notifId)
      if (n) n.leido = true
      updateNativeAppBadge(this.unreadCount)
    },
    markAllRead() {
      this.unreadCount = 0
      this.notifications.forEach(n => (n.leido = true))
      updateNativeAppBadge(0)
    },
    clearAll() {
      this.notifications = []
      this.unreadCount = 0
      updateNativeAppBadge(0)
    },
    startPolling() {
      if (this.pollTimer) return
      this.fetchUnreadCount()
      this.pollTimer = setInterval(() => this.fetchUnreadCount(), 5000)

      this._syncFn = () => {
        if (document.visibilityState === 'visible') {
          this.fetchUnreadCount()
        }
      }
      window.addEventListener('focus', this._syncFn)
      document.addEventListener('visibilitychange', this._syncFn)
    },
    stopPolling() {
      if (this.pollTimer) {
        clearInterval(this.pollTimer)
        this.pollTimer = null
      }
      if (this._syncFn) {
        window.removeEventListener('focus', this._syncFn)
        document.removeEventListener('visibilitychange', this._syncFn)
        this._syncFn = null
      }
    },
  },
})
